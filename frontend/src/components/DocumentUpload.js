import React, { useState } from 'react';
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
  Icon
} from '@chakra-ui/react';
import { FiUpload, FiFile } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const DocumentUpload = ({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const toast = useToast();
  const { getToken } = useAuth();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
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

      // Add metadata if needed
      // formData.append('metadata', JSON.stringify({ key: 'value' }));

      const response = await api.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
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

      // Reset form
      setSelectedFile(null);
      
      // Call the success callback if provided
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
    } catch (error) {
      console.error('Upload error:', error);
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
    <Box p={4} borderWidth="1px" borderRadius="lg" bg="white" shadow="md">
      <VStack spacing={4} align="stretch">
        <Text fontSize="xl" fontWeight="bold">Upload Document</Text>
        
        <FormControl>
          <FormLabel>Select a document to upload</FormLabel>
          <Input
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.txt,.doc,.docx,.jpg,.jpeg,.png"
            p={1}
            disabled={isUploading}
          />
          <Text fontSize="sm" color="gray.500" mt={1}>
            Supported formats: PDF, TXT, DOC, DOCX, JPG, PNG (Max 10MB)
          </Text>
        </FormControl>

        {selectedFile && (
          <Flex align="center">
            <Icon as={FiFile} mr={2} />
            <Text isTruncated>{selectedFile.name}</Text>
            <Text ml={2} fontSize="sm" color="gray.500">
              ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </Text>
          </Flex>
        )}

        {isUploading && (
          <Box>
            <Text mb={1}>Uploading... {uploadProgress}%</Text>
            <Progress value={uploadProgress} size="sm" colorScheme="blue" />
          </Box>
        )}

        <Button
          leftIcon={<FiUpload />}
          colorScheme="blue"
          onClick={handleUpload}
          isLoading={isUploading}
          loadingText="Uploading"
          disabled={!selectedFile || isUploading}
        >
          Upload Document
        </Button>
      </VStack>
    </Box>
  );
};

export default DocumentUpload;
