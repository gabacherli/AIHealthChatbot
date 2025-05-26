import React, { useRef, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Collapse,
  Button,
  Icon,
  Divider,
  useColorModeValue,
  Tooltip
} from '@chakra-ui/react';
import { FiUser, FiBot, FiFileText, FiChevronDown, FiChevronUp, FiClock, FiDatabase } from 'react-icons/fi';
import { useAuth } from '../../../auth/hooks/useAuth';
import ReactMarkdown from 'react-markdown';

/**
 * Enhanced message list component for displaying chat messages with medical context
 */
const MessageList = ({ messages }) => {
  const { user } = useAuth();
  const messagesEndRef = useRef(null);
  const [expandedSources, setExpandedSources] = useState({});

  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.800');
  const userBg = useColorModeValue('blue.500', 'blue.600');
  const botBg = useColorModeValue('gray.100', 'gray.700');
  const errorBg = useColorModeValue('red.100', 'red.900');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textSecondary = useColorModeValue('gray.600', 'gray.400');

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Scroll to the bottom of the message list
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  /**
   * Toggle source expansion for a message
   */
  const toggleSources = (messageId) => {
    setExpandedSources(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }));
  };

  /**
   * Format timestamp for display
   */
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  /**
   * Render message sources
   */
  const renderSources = (message) => {
    if (!message.sources || message.sources.length === 0) return null;

    const isExpanded = expandedSources[message.id];

    return (
      <Box mt={3}>
        <Button
          size="sm"
          variant="ghost"
          leftIcon={<Icon as={FiFileText} />}
          rightIcon={<Icon as={isExpanded ? FiChevronUp : FiChevronDown} />}
          onClick={() => toggleSources(message.id)}
          colorScheme="blue"
        >
          {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
        </Button>

        <Collapse in={isExpanded}>
          <Box mt={2} p={3} bg={useColorModeValue('blue.50', 'blue.900')} borderRadius="md">
            <VStack spacing={2} align="stretch">
              {message.sources.map((source, index) => (
                <Box key={index} p={2} bg={bgColor} borderRadius="sm" borderWidth="1px" borderColor={borderColor}>
                  <VStack spacing={1} align="stretch">
                    <HStack justify="space-between">
                      <Text fontSize="sm" fontWeight="medium" noOfLines={1}>
                        {source.source}
                      </Text>
                      <Badge size="sm" colorScheme="blue">
                        {(source.score * 100).toFixed(0)}% match
                      </Badge>
                    </HStack>

                    <HStack spacing={2} fontSize="xs" color={textSecondary}>
                      <Text>{source.content_type}</Text>
                      {source.upload_date && (
                        <>
                          <Text>•</Text>
                          <Text>{new Date(source.upload_date).toLocaleDateString()}</Text>
                        </>
                      )}
                    </HStack>

                    {source.medical_keywords && (
                      <HStack spacing={1} mt={1}>
                        {source.medical_keywords.slice(0, 3).map((keyword, i) => (
                          <Badge key={i} size="xs" colorScheme="green">
                            {keyword}
                          </Badge>
                        ))}
                        {source.medical_keywords.length > 3 && (
                          <Badge size="xs" variant="outline">
                            +{source.medical_keywords.length - 3} more
                          </Badge>
                        )}
                      </HStack>
                    )}

                    {source.has_medical_image && (
                      <Badge size="xs" colorScheme="purple">
                        Medical Image
                      </Badge>
                    )}
                  </VStack>
                </Box>
              ))}
            </VStack>
          </Box>
        </Collapse>
      </Box>
    );
  };

  /**
   * Render individual message
   */
  const renderMessage = (message, index) => {
    const isUser = message.sender === 'user';
    const isError = message.isError;

    return (
      <Box key={message.id || index} mb={4}>
        <HStack spacing={3} align="flex-start">
          {/* Avatar */}
          <Box
            p={2}
            borderRadius="full"
            bg={isUser ? userBg : (isError ? errorBg : botBg)}
            color={isUser ? 'white' : (isError ? 'red.600' : textSecondary)}
          >
            <Icon as={isUser ? FiUser : FiBot} boxSize={4} />
          </Box>

          {/* Message Content */}
          <Box flex={1} maxW="calc(100% - 60px)">
            <VStack spacing={2} align="stretch">
              {/* Message Header */}
              <HStack justify="space-between" align="center">
                <Text fontSize="sm" fontWeight="medium" color={textSecondary}>
                  {isUser ? (user?.role === 'professional' ? 'Healthcare Professional' : 'Patient') : 'AI Assistant'}
                </Text>
                <HStack spacing={2} fontSize="xs" color={textSecondary}>
                  <Icon as={FiClock} />
                  <Text>{formatTimestamp(message.timestamp)}</Text>
                  {message.hasDocumentContext && (
                    <Tooltip label="Response includes medical document context">
                      <Icon as={FiDatabase} color="blue.500" />
                    </Tooltip>
                  )}
                </HStack>
              </HStack>

              {/* Message Text */}
              <Box
                p={3}
                bg={isUser ? userBg : (isError ? errorBg : botBg)}
                color={isUser ? 'white' : (isError ? 'red.600' : 'inherit')}
                borderRadius="lg"
                borderTopLeftRadius={isUser ? 'lg' : 'sm'}
                borderTopRightRadius={isUser ? 'sm' : 'lg'}
              >
                {message.sender === 'bot' ? (
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                ) : (
                  <Text>{message.text}</Text>
                )}
              </Box>

              {/* Patient Context Indicator */}
              {message.patientContext && (
                <Badge size="sm" colorScheme="blue" alignSelf="flex-start">
                  Patient Context: ID {message.patientContext.patientId}
                </Badge>
              )}

              {/* Sources */}
              {renderSources(message)}

              {/* Metadata for professionals */}
              {user?.role === 'professional' && message.metadata && (
                <Text fontSize="xs" color={textSecondary}>
                  Sources: {message.metadata.sources_count || 0} •
                  Context: {message.metadata.has_medical_context ? 'Yes' : 'No'}
                </Text>
              )}
            </VStack>
          </Box>
        </HStack>
      </Box>
    );
  };

  return (
    <Box p={4} minH="400px">
      {messages.length === 0 ? (
        <VStack spacing={4} py={8} textAlign="center">
          <Icon as={FiBot} boxSize={12} color="blue.500" />
          <VStack spacing={2}>
            <Text fontSize="xl" fontWeight="bold" color="blue.500">
              Welcome to the AI Health Chatbot!
            </Text>
            <Text color={textSecondary} maxW="md">
              {user?.role === 'professional'
                ? 'Ask medical questions to get detailed clinical insights with document context from your patients.'
                : 'Ask health-related questions for personalized answers based on your medical history.'}
            </Text>
          </VStack>
        </VStack>
      ) : (
        <VStack spacing={0} align="stretch">
          {messages.map(renderMessage)}
        </VStack>
      )}
      <div ref={messagesEndRef} />
    </Box>
  );
};

MessageList.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      text: PropTypes.string.isRequired,
      sender: PropTypes.oneOf(['user', 'bot']).isRequired,
      timestamp: PropTypes.string.isRequired,
      isError: PropTypes.bool,
      sources: PropTypes.arrayOf(PropTypes.object),
      metadata: PropTypes.object,
      hasContext: PropTypes.bool,
      hasDocumentContext: PropTypes.bool,
      sourcesCount: PropTypes.number,
      patientContext: PropTypes.object
    })
  ).isRequired
};

export default MessageList;
