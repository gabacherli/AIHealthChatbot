import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  Heading,
  Text,
  VStack,
  HStack,
  Icon,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  Card,
  CardBody,
  Badge,
  Flex,
  useColorModeValue,
  SimpleGrid,
  Stack,
  Divider,
  Tooltip,
} from '@chakra-ui/react';
import { FiDownload, FiTrash2, FiFile, FiRefreshCw, FiFileText, FiImage, FiUpload, FiCalendar, FiHardDrive } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

// CSS keyframes for smooth refresh animation
const refreshKeyframes = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;

// Helper function to get file icon based on file type
const getFileIcon = (filename) => {
  const extension = filename.split('.').pop()?.toLowerCase();
  switch (extension) {
    case 'pdf':
      return FiFile;
    case 'txt':
      return FiFileText;
    case 'jpg':
    case 'jpeg':
    case 'png':
      return FiImage;
    case 'doc':
    case 'docx':
      return FiFileText;
    default:
      return FiFile;
  }
};

// Helper function to get file type badge color
const getFileTypeBadge = (filename) => {
  const extension = filename.split('.').pop()?.toLowerCase();
  switch (extension) {
    case 'pdf':
      return { color: 'red', label: 'PDF' };
    case 'txt':
      return { color: 'blue', label: 'TXT' };
    case 'jpg':
    case 'jpeg':
    case 'png':
      return { color: 'green', label: 'IMG' };
    case 'doc':
    case 'docx':
      return { color: 'purple', label: 'DOC' };
    default:
      return { color: 'gray', label: 'FILE' };
  }
};

// Helper function to format file size
const formatFileSize = (bytes) => {
  if (!bytes) return 'Unknown size';
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};

// Helper function to format relative time
const formatRelativeTime = (date) => {
  if (!date) return 'Unknown date';

  const now = new Date();
  const diffInMs = now - new Date(date);
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
  const diffInMinutes = Math.floor(diffInMs / (1000 * 60));

  if (diffInDays > 7) {
    return new Date(date).toLocaleDateString();
  } else if (diffInDays > 0) {
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  } else if (diffInHours > 0) {
    return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
  } else if (diffInMinutes > 0) {
    return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
  } else {
    return 'Just now';
  }
};

// Helper function to get enhanced file type information
const getEnhancedFileType = (filename) => {
  const extension = filename.split('.').pop()?.toLowerCase();
  switch (extension) {
    case 'pdf':
      return { type: 'PDF Document', category: 'document' };
    case 'txt':
      return { type: 'Text Document', category: 'document' };
    case 'jpg':
    case 'jpeg':
      return { type: 'JPEG Image', category: 'image' };
    case 'png':
      return { type: 'PNG Image', category: 'image' };
    case 'doc':
      return { type: 'Word Document', category: 'document' };
    case 'docx':
      return { type: 'Word Document', category: 'document' };
    case 'csv':
      return { type: 'CSV Spreadsheet', category: 'spreadsheet' };
    case 'xlsx':
    case 'xls':
      return { type: 'Excel Spreadsheet', category: 'spreadsheet' };
    default:
      return { type: 'Document', category: 'file' };
  }
};

const DocumentList = ({ onDocumentDeleted }) => {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  const { getToken } = useAuth();

  // Color mode values for better theming
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');
  const cardHoverBg = useColorModeValue('gray.50', 'gray.700');
  const textSecondary = useColorModeValue('gray.600', 'gray.400');
  const emptyStateBg = useColorModeValue('gray.50', 'gray.700');

  // Modal-specific color mode values
  const modalBorderColor = useColorModeValue('gray.300', 'gray.600');
  const iconContainerBg = useColorModeValue('red.50', 'red.900');
  const iconContainerBorder = useColorModeValue('red.100', 'red.800');
  const headerTextColor = useColorModeValue('gray.900', 'white');
  const cancelButtonHoverBg = useColorModeValue('gray.100', 'gray.700');

  // Refresh icon color mode values
  const refreshIconHoverColor = useColorModeValue('gray.700', 'gray.300');

  // Empty state color mode values
  const emptyStateHoverBorder = useColorModeValue('gray.400', 'gray.500');
  const emptyStateIconBg = useColorModeValue('blue.50', 'blue.900');
  const emptyStateIconBorder = useColorModeValue('blue.100', 'blue.800');
  const emptyStateHeadingColor = useColorModeValue('gray.800', 'gray.200');

  // Card hover and focus color mode values
  const cardHoverBorderColor = useColorModeValue('gray.300', 'gray.500');
  const cardFocusBoxShadow = useColorModeValue('blue.100', 'blue.800');

  // Button hover and focus color mode values
  const downloadButtonHoverBg = useColorModeValue('blue.50', 'blue.900');
  const downloadButtonFocusBoxShadow = useColorModeValue('blue.200', 'blue.600');
  const deleteButtonHoverBg = useColorModeValue('red.50', 'red.900');
  const deleteButtonFocusBoxShadow = useColorModeValue('red.200', 'red.600');

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = await getToken();

      const response = await api.get('/documents/list', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const docs = response.data.documents || [];
      setDocuments(docs);
      setLastRefreshed(new Date());
    } catch (err) {
      console.error('❌ Error fetching documents:', err);
      setError('Failed to load documents. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Add a method to manually refresh documents
  const refreshDocuments = useCallback(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Expose refresh method to parent component
  useEffect(() => {
    window.refreshDocumentList = refreshDocuments;

    return () => {
      delete window.refreshDocumentList;
    };
  }, [refreshDocuments]);

  const handleDownload = async (filename) => {
    try {
      const token = await getToken();

      // Create a temporary anchor element
      const link = document.createElement('a');
      link.href = `${api.defaults.baseURL}/documents/download/${filename}`;
      link.setAttribute('download', filename);
      link.setAttribute('target', '_blank');

      // Add authorization header via fetch
      fetch(link.href, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        link.href = url;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      });
    } catch (err) {
      console.error('Error downloading document:', err);
      toast({
        title: 'Download failed',
        description: 'Failed to download the document',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const confirmDelete = (document) => {
    setSelectedDocument(document);
    onOpen();
  };

  const handleDelete = async () => {
    if (!selectedDocument) return;

    try {
      const token = await getToken();
      await api.delete(`/documents/delete/${selectedDocument.filename}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      // Remove the document from the list
      setDocuments(documents.filter(doc => doc.filename !== selectedDocument.filename));

      toast({
        title: 'Document deleted',
        description: 'The document has been successfully deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Call the callback if provided
      if (onDocumentDeleted) {
        onDocumentDeleted(selectedDocument);
      }
    } catch (err) {
      console.error('Error deleting document:', err);
      toast({
        title: 'Delete failed',
        description: err.response?.data?.error || 'Failed to delete the document',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      onClose();
      setSelectedDocument(null);
    }
  };

  if (isLoading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading documents...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        <AlertTitle mr={2}>Error!</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <Box>
      {/* Inject CSS keyframes for refresh animation */}
      <style>
        {refreshKeyframes}
      </style>

      {/* Header Section */}
      <Flex
        justifyContent="space-between"
        alignItems={{ base: "flex-start", md: "center" }}
        direction={{ base: "column", md: "row" }}
        gap={4}
        mb={6}
      >
        <Box>
          <Heading size="lg" mb={2}>Your Documents</Heading>
          <Text color={textSecondary} fontSize="sm">
            {documents.length} {documents.length === 1 ? 'document' : 'documents'} uploaded
          </Text>
        </Box>

        {/* Discrete Refresh Control */}
        <VStack spacing={1} align={{ base: "flex-start", md: "flex-end" }}>
          <HStack spacing={2} align="center">
            <Icon
              as={FiRefreshCw}
              boxSize={4}
              color={textSecondary}
              cursor="pointer"
              onClick={fetchDocuments}
              _hover={{
                color: refreshIconHoverColor,
                transform: !isLoading ? 'rotate(180deg)' : undefined
              }}
              transition={isLoading ? 'none' : 'all 0.3s ease'}
              animation={isLoading ? 'spin 1s linear infinite' : 'none'}
              _focus={{
                outline: 'none',
                boxShadow: `0 0 0 2px ${refreshIconHoverColor}`
              }}
              aria-label="Refresh documents"
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  fetchDocuments();
                }
              }}
            />
            <Text fontSize="xs" color={textSecondary} fontWeight="medium">
              Refresh
            </Text>
          </HStack>
          {lastRefreshed && (
            <Text fontSize="xs" color={textSecondary}>
              Last updated {lastRefreshed.toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </Text>
          )}
        </VStack>
      </Flex>

      {/* Enhanced Empty State with Modern Design */}
      {documents.length === 0 ? (
        <Card
          bg={emptyStateBg}
          borderStyle="dashed"
          borderWidth="3px"
          borderColor={cardBorder}
          borderRadius="2xl"
          transition="all 0.3s"
          _hover={{
            borderColor: emptyStateHoverBorder,
            transform: "translateY(-2px)",
            shadow: "lg"
          }}
        >
          <CardBody textAlign="center" py={20} px={8}>
            <VStack spacing={8}>
              <Box
                p={6}
                borderRadius="2xl"
                bg={emptyStateIconBg}
                border="3px solid"
                borderColor={emptyStateIconBorder}
                shadow="lg"
              >
                <Icon as={FiUpload} boxSize={12} color="blue.500" />
              </Box>

              <VStack spacing={4}>
                <Heading size="xl" color={emptyStateHeadingColor} fontWeight="bold">
                  No documents yet
                </Heading>
                <Text color={textSecondary} fontSize="lg" lineHeight="1.7" maxW="lg" fontWeight="medium">
                  Upload your first medical document to unlock AI-powered health insights and personalized recommendations
                </Text>
              </VStack>

              <VStack spacing={3}>
                <Text fontSize="md" color={textSecondary} fontWeight="semibold">
                  Supported formats: PDF, TXT, DOC, DOCX, JPG, PNG
                </Text>
                <Text fontSize="sm" color={textSecondary}>
                  Navigate to the "Upload New" tab to get started
                </Text>
              </VStack>
            </VStack>
          </CardBody>
        </Card>
      ) : (
        /* Enhanced Document Grid - Google Drive Style */
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
          {documents.map((doc) => {
            const fileIcon = getFileIcon(doc.filename);
            const fileBadge = getFileTypeBadge(doc.filename);
            const enhancedFileType = getEnhancedFileType(doc.filename);

            return (
              <Card
                key={doc.id || doc.filename}
                bg={cardBg}
                borderColor={cardBorder}
                borderWidth="1px"
                borderRadius="xl"
                _hover={{
                  bg: cardHoverBg,
                  transform: "translateY(-2px)",
                  shadow: "xl",
                  borderColor: cardHoverBorderColor
                }}
                transition="all 0.3s ease-in-out"
                cursor="pointer"
                _focus={{
                  outline: 'none',
                  boxShadow: `0 0 0 3px ${cardFocusBoxShadow}`
                }}
                tabIndex={0}
                role="button"
                aria-label={`Document: ${doc.filename}`}
                overflow="hidden"
              >
                <CardBody p={6}>
                  <Stack spacing={5}>
                    {/* Enhanced File Header with Larger Icon */}
                    <Flex alignItems="flex-start" justifyContent="space-between">
                      <HStack spacing={4} flex={1} minW={0}>
                        {/* Larger, More Prominent Icon */}
                        <Box
                          p={3}
                          borderRadius="xl"
                          bg={`${fileBadge.color}.50`}
                          border="2px solid"
                          borderColor={`${fileBadge.color}.100`}
                          _dark={{
                            bg: `${fileBadge.color}.900`,
                            borderColor: `${fileBadge.color}.800`
                          }}
                          flexShrink={0}
                        >
                          <Icon
                            as={fileIcon}
                            color={`${fileBadge.color}.500`}
                            boxSize={10} // Increased from 6 to 10 (40px)
                          />
                        </Box>

                        {/* Enhanced File Information */}
                        <Box flex={1} minW={0}>
                          <Tooltip label={doc.filename} placement="top" hasArrow>
                            <Text
                              fontWeight="bold"
                              fontSize="lg"
                              noOfLines={1}
                              title={doc.filename}
                              color={headerTextColor}
                              lineHeight="1.2"
                            >
                              {doc.filename}
                            </Text>
                          </Tooltip>

                          {/* Enhanced Metadata Row */}
                          <VStack spacing={2} align="flex-start" mt={2}>
                            <HStack spacing={3} wrap="wrap">
                              <Badge
                                colorScheme={fileBadge.color}
                                size="md"
                                variant="solid"
                                borderRadius="lg"
                                px={3}
                                py={1}
                                fontWeight="semibold"
                              >
                                {fileBadge.label}
                              </Badge>
                              <Text fontSize="sm" color={textSecondary} fontWeight="medium">
                                {enhancedFileType.type}
                              </Text>
                            </HStack>

                            {/* File Details Row */}
                            <HStack spacing={4} fontSize="xs" color={textSecondary}>
                              {/* File Size */}
                              <HStack spacing={1}>
                                <Icon as={FiHardDrive} boxSize={3} />
                                <Text>
                                  {doc.metadata?.size ? formatFileSize(doc.metadata.size) : 'Size unknown'}
                                </Text>
                              </HStack>

                              {/* Upload Date */}
                              <HStack spacing={1}>
                                <Icon as={FiCalendar} boxSize={3} />
                                <Text>
                                  {doc.metadata?.upload_date ? formatRelativeTime(doc.metadata.upload_date) : 'Recently added'}
                                </Text>
                              </HStack>
                            </HStack>
                          </VStack>
                        </Box>
                      </HStack>
                    </Flex>

                    <Divider opacity={0.6} />

                    {/* Enhanced Action Buttons with Better Styling */}
                    <Flex
                      direction={{ base: "column", sm: "row" }}
                      gap={3}
                      justifyContent="flex-end"
                      pt={1}
                    >
                      <Button
                        size="md"
                        leftIcon={<FiDownload />}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDownload(doc.filename);
                        }}
                        colorScheme="blue"
                        variant="outline"
                        flex={{ base: 1, sm: "none" }}
                        borderRadius="lg"
                        borderWidth="2px"
                        fontWeight="semibold"
                        _hover={{
                          bg: downloadButtonHoverBg,
                          transform: "translateY(-2px)",
                          shadow: "md"
                        }}
                        _focus={{
                          boxShadow: `0 0 0 3px ${downloadButtonFocusBoxShadow}`
                        }}
                        transition="all 0.2s"
                        aria-label={`Download ${doc.filename}`}
                      >
                        Download
                      </Button>
                      <Button
                        size="md"
                        leftIcon={<FiTrash2 />}
                        onClick={(e) => {
                          e.stopPropagation();
                          confirmDelete(doc);
                        }}
                        colorScheme="red"
                        variant="outline"
                        flex={{ base: 1, sm: "none" }}
                        borderRadius="lg"
                        borderWidth="2px"
                        fontWeight="semibold"
                        _hover={{
                          bg: deleteButtonHoverBg,
                          transform: "translateY(-2px)",
                          shadow: "md"
                        }}
                        _focus={{
                          boxShadow: `0 0 0 3px ${deleteButtonFocusBoxShadow}`
                        }}
                        transition="all 0.2s"
                        aria-label={`Delete ${doc.filename}`}
                      >
                        Delete
                      </Button>
                    </Flex>
                  </Stack>
                </CardBody>
              </Card>
            );
          })}
        </SimpleGrid>
      )}

      {/* Enhanced Delete Confirmation Modal */}
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        isCentered
        motionPreset="slideInBottom"
        size={{ base: "sm", md: "md" }}
        preserveScrollBarGap
        scrollBehavior="inside"
      >
        <ModalOverlay
          bg="blackAlpha.600"
          backdropFilter="blur(10px)"
        />
        <ModalContent
          mx={4}
          my={4}
          bg={cardBg}
          borderRadius="3xl"
          shadow="2xl"
          borderWidth="2px"
          borderColor={modalBorderColor}
          overflow="hidden"
          maxH="90vh"
        >
          <ModalHeader pb={3} pt={6} px={6}>
            <HStack spacing={3} align="center">
              <Box
                p={2}
                borderRadius="lg"
                bg={iconContainerBg}
                border="1px solid"
                borderColor={iconContainerBorder}
              >
                <Icon as={FiTrash2} color="red.500" boxSize={5} />
              </Box>
              <Box>
                <Text fontSize="lg" fontWeight="semibold" color={headerTextColor}>
                  Confirm Deletion
                </Text>
                <Text fontSize="sm" color={textSecondary} mt={1}>
                  This action cannot be undone
                </Text>
              </Box>
            </HStack>
          </ModalHeader>

          <ModalBody pb={6} px={6}>
            <VStack spacing={5} align="stretch">
              <Text color={textSecondary} fontSize="md" lineHeight="1.6">
                Are you sure you want to delete this document? All associated data will be permanently removed.
              </Text>

              {selectedDocument && (
                <Card
                  bg={emptyStateBg}
                  borderWidth="1px"
                  borderColor={cardBorder}
                  borderRadius="xl"
                  shadow="sm"
                  transition="all 0.2s"
                  _hover={{ shadow: "md" }}
                >
                  <CardBody p={5}>
                    <HStack spacing={4}>
                      <Box
                        p={2}
                        borderRadius="lg"
                        bg={`${getFileTypeBadge(selectedDocument.filename).color}.50`}
                        border="1px solid"
                        borderColor={`${getFileTypeBadge(selectedDocument.filename).color}.100`}
                        _dark={{
                          bg: `${getFileTypeBadge(selectedDocument.filename).color}.900`,
                          borderColor: `${getFileTypeBadge(selectedDocument.filename).color}.800`
                        }}
                      >
                        <Icon
                          as={getFileIcon(selectedDocument.filename)}
                          color={`${getFileTypeBadge(selectedDocument.filename).color}.500`}
                          boxSize={5}
                        />
                      </Box>
                      <Box flex={1} minW={0}>
                        <Text fontWeight="semibold" noOfLines={1} fontSize="md">
                          {selectedDocument.filename}
                        </Text>
                        <Text fontSize="sm" color={textSecondary} mt={1}>
                          {selectedDocument.metadata?.content_type || 'Document'}
                        </Text>
                      </Box>
                    </HStack>
                  </CardBody>
                </Card>
              )}
            </VStack>
          </ModalBody>

          <ModalFooter pt={0} pb={6} px={6}>
            <Stack
              direction={{ base: "column", sm: "row" }}
              spacing={3}
              width="full"
              justifyContent="flex-end"
            >
              <Button
                variant="ghost"
                onClick={onClose}
                flex={{ base: 1, sm: "none" }}
                size="md"
                borderRadius="lg"
                _hover={{ bg: cancelButtonHoverBg }}
              >
                Cancel
              </Button>
              <Button
                colorScheme="red"
                onClick={handleDelete}
                leftIcon={<FiTrash2 />}
                flex={{ base: 1, sm: "none" }}
                isLoading={false}
                loadingText="Deleting..."
                size="md"
                borderRadius="lg"
                shadow="sm"
                _hover={{ shadow: "md", transform: "translateY(-1px)" }}
                transition="all 0.2s"
              >
                Delete Document
              </Button>
            </Stack>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default DocumentList;
