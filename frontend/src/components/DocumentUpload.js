import { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Text,
  useToast,
  Progress,
  Flex,
  Icon,
  Card,
  CardBody,
  HStack,
  Badge,
  useColorModeValue,
  Stack,
  Divider,
  Alert,
  AlertIcon,
  Heading,
} from '@chakra-ui/react';
import { FiUpload, FiFile, FiFileText, FiImage, FiCheck } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

// Helper function to get file icon
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

// Helper function to get file type badge
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

const DocumentUpload = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const toast = useToast();
  const { getToken } = useAuth();

  // Color mode values
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');
  const dropzoneBg = useColorModeValue('gray.50', 'gray.700');
  const dropzoneBorder = useColorModeValue('gray.300', 'gray.600');
  const textSecondary = useColorModeValue('gray.600', 'gray.400');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadSuccess(false);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast({
        title: 'No file selected',
        description: 'Please select a file to upload',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    // Check file size (limit to 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'Maximum file size is 10MB',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    // Check file type
    const allowedTypes = [
      'application/pdf',
      'text/plain',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'image/jpeg',
      'image/png'
    ];

    if (!allowedTypes.includes(selectedFile.type)) {
      toast({
        title: 'Invalid file type',
        description: 'Please upload a PDF, TXT, DOC, DOCX, JPG, or PNG file',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const token = await getToken();

      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await api.post('/documents/upload', formData, {
        headers: {
          // Don't set Content-Type for multipart/form-data - let browser set it with boundary
          'Authorization': `Bearer ${token}`
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        }
      });

      toast({
        title: 'Upload successful',
        description: 'Your document has been uploaded and processed',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Trigger refresh of document list
      if (window.refreshDocumentList) {
        window.refreshDocumentList();
      }

      // Set success state
      setUploadSuccess(true);

      // Reset form after a delay
      setTimeout(() => {
        setSelectedFile(null);
        setUploadProgress(0);
        setUploadSuccess(false);
      }, 2000);

      // Call the success callback if provided
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
    } catch (error) {
      console.error('❌ Upload error:', error);

      toast({
        title: 'Upload failed',
        description: error.response?.data?.error || 'An error occurred during upload',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px" shadow="md">
      <CardBody p={6}>
        <VStack spacing={6} align="stretch">
          {/* Header */}
          <Box>
            <Heading size="md" mb={2}>Upload Document</Heading>
            <Text color={textSecondary} fontSize="sm">
              Upload medical documents for AI-powered health insights
            </Text>
          </Box>

          <Divider />

          {/* File Upload Section */}
          <FormControl>
            <FormLabel fontWeight="medium">Select a document</FormLabel>
            <Box
              p={6}
              borderWidth="2px"
              borderStyle="dashed"
              borderColor={selectedFile ? "blue.300" : dropzoneBorder}
              borderRadius="lg"
              bg={selectedFile ? "blue.50" : dropzoneBg}
              textAlign="center"
              transition="all 0.2s"
              _hover={{
                borderColor: "blue.400",
                bg: "blue.50"
              }}
            >
              <Input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.txt,.doc,.docx,.jpg,.jpeg,.png"
                position="absolute"
                opacity={0}
                width="100%"
                height="100%"
                cursor="pointer"
                disabled={isUploading}
              />
              <VStack spacing={3}>
                <Icon
                  as={FiUpload}
                  boxSize={8}
                  color={selectedFile ? "blue.500" : textSecondary}
                />
                <Text fontWeight="medium" color={selectedFile ? "blue.600" : textSecondary}>
                  {selectedFile ? "File selected" : "Click to browse or drag and drop"}
                </Text>
                <Text fontSize="sm" color={textSecondary}>
                  PDF, TXT, DOC, DOCX, JPG, PNG (Max 10MB)
                </Text>
              </VStack>
            </Box>
          </FormControl>

          {/* Selected File Display */}
          {selectedFile && (
            <Card bg={dropzoneBg} borderWidth="1px" borderColor={cardBorder}>
              <CardBody p={4}>
                <HStack spacing={3}>
                  <Icon
                    as={getFileIcon(selectedFile.name)}
                    color={`${getFileTypeBadge(selectedFile.name).color}.500`}
                    boxSize={5}
                  />
                  <Box flex={1} minW={0}>
                    <Text fontWeight="medium" noOfLines={1}>
                      {selectedFile.name}
                    </Text>
                    <HStack spacing={2} mt={1}>
                      <Badge
                        colorScheme={getFileTypeBadge(selectedFile.name).color}
                        size="sm"
                        variant="subtle"
                      >
                        {getFileTypeBadge(selectedFile.name).label}
                      </Badge>
                      <Text fontSize="xs" color={textSecondary}>
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </Text>
                    </HStack>
                  </Box>
                  {uploadSuccess && (
                    <Icon as={FiCheck} color="green.500" boxSize={5} />
                  )}
                </HStack>
              </CardBody>
            </Card>
          )}

          {/* Upload Progress */}
          {isUploading && (
            <Box>
              <Flex justifyContent="space-between" mb={2}>
                <Text fontSize="sm" fontWeight="medium">Uploading...</Text>
                <Text fontSize="sm" color={textSecondary}>{uploadProgress}%</Text>
              </Flex>
              <Progress
                value={uploadProgress}
                size="md"
                colorScheme="blue"
                borderRadius="full"
              />
            </Box>
          )}

          {/* Success Message */}
          {uploadSuccess && (
            <Alert status="success" borderRadius="lg">
              <AlertIcon />
              <Box>
                <Text fontWeight="medium">Upload successful!</Text>
                <Text fontSize="sm">Your document has been processed and is ready for analysis.</Text>
              </Box>
            </Alert>
          )}

          {/* Upload Button */}
          <Stack direction={{ base: "column", sm: "row" }} spacing={3}>
            <Button
              leftIcon={<FiUpload />}
              colorScheme="blue"
              onClick={handleUpload}
              isLoading={isUploading}
              loadingText="Uploading..."
              disabled={!selectedFile || isUploading || uploadSuccess}
              flex={1}
              size="lg"
            >
              {uploadSuccess ? "Upload Complete" : "Upload Document"}
            </Button>
            {selectedFile && !isUploading && (
              <Button
                variant="outline"
                onClick={() => {
                  setSelectedFile(null);
                  setUploadSuccess(false);
                  setUploadProgress(0);
                }}
                size="lg"
              >
                Clear
              </Button>
            )}
          </Stack>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default DocumentUpload;
