import React, { useState } from 'react';
import {
  Container,
  VStack,
  Box,
  Heading,
  Text,
  HStack,
  Badge,
  useColorModeValue,
  Divider
} from '@chakra-ui/react';
import { useAuth } from '../../features/auth/hooks/useAuth';
import { useChat } from '../../features/chat/hooks/useChat';
import MessageList from '../../features/chat/components/MessageList';
import ChatInput from '../../features/chat/components/ChatInput';
import PatientSelector from '../../features/chat/components/PatientSelector';

/**
 * Enhanced chat page component with document retrieval and patient context
 */
const ChatPage = () => {
  const { user } = useAuth();
  const { messages, loading, sendMessage } = useChat();
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState(null);

  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textSecondary = useColorModeValue('gray.600', 'gray.400');

  const handlePatientChange = (patientId, patient) => {
    setSelectedPatientId(patientId);
    setSelectedPatient(patient);
  };

  const handleSendMessage = async (message) => {
    // Pass patient context to the chat service
    return await sendMessage(message, selectedPatientId);
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'professional':
        return 'blue';
      case 'patient':
        return 'green';
      default:
        return 'gray';
    }
  };

  return (
    <Container maxW="4xl" py={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box
          p={6}
          bg={bgColor}
          borderWidth="1px"
          borderColor={borderColor}
          borderRadius="lg"
          shadow="sm"
        >
          <VStack spacing={3} align="stretch">
            <HStack justify="space-between" align="center">
              <Heading size="lg" color="blue.500">
                AI Health Chatbot
              </Heading>
              <HStack spacing={3}>
                <Text fontSize="sm" color={textSecondary}>
                  Logged in as:
                </Text>
                <Badge colorScheme={getRoleBadgeColor(user?.role)} size="lg">
                  {user?.role || 'User'}
                </Badge>
              </HStack>
            </HStack>

            {user?.role === 'professional' && (
              <Text fontSize="sm" color={textSecondary}>
                Select a patient below to include their medical documents in the conversation context.
              </Text>
            )}
          </VStack>
        </Box>

        {/* Patient Selector for Healthcare Professionals */}
        {user?.role === 'professional' && (
          <PatientSelector
            selectedPatientId={selectedPatientId}
            onPatientChange={handlePatientChange}
            disabled={loading}
          />
        )}

        {/* Chat Interface */}
        <Box
          bg={bgColor}
          borderWidth="1px"
          borderColor={borderColor}
          borderRadius="lg"
          shadow="sm"
          overflow="hidden"
          minH="500px"
          display="flex"
          flexDirection="column"
        >
          {/* Messages Area */}
          <Box flex={1} p={4}>
            <MessageList messages={messages} />
          </Box>

          <Divider />

          {/* Input Area */}
          <Box p={4}>
            <ChatInput
              onSendMessage={handleSendMessage}
              loading={loading}
              placeholder={
                user?.role === 'professional' && selectedPatient
                  ? `Ask about ${selectedPatient.full_name}'s health...`
                  : "Ask a health-related question..."
              }
            />
          </Box>
        </Box>

        {/* Context Info */}
        {user?.role === 'professional' && selectedPatient && (
          <Box
            p={4}
            bg={useColorModeValue('blue.50', 'blue.900')}
            borderWidth="1px"
            borderColor={useColorModeValue('blue.200', 'blue.700')}
            borderRadius="md"
          >
            <Text fontSize="sm" color={useColorModeValue('blue.700', 'blue.200')}>
              <strong>Active Context:</strong> Responses will include medical documents and history
              from {selectedPatient.full_name}'s records.
            </Text>
          </Box>
        )}
      </VStack>
    </Container>
  );
};

export default ChatPage;
