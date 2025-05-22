import React, { useState, useEffect } from 'react';
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
  ModalCloseButton,
} from '@chakra-ui/react';
import { FiDownload, FiTrash2, FiFile, FiRefreshCw } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const DocumentList = ({ onDocumentDeleted }) => {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  const { getToken } = useAuth();

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = await getToken();
      const response = await api.get('/api/documents/list', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      setDocuments(response.data.documents || []);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleDownload = async (filename) => {
    try {
      const token = await getToken();
      
      // Create a temporary anchor element
      const link = document.createElement('a');
      link.href = `${api.defaults.baseURL}/api/documents/download/${filename}`;
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
      await api.delete(`/api/documents/delete/${selectedDocument.filename}`, {
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
      <HStack justifyContent="space-between" mb={4}>
        <Heading size="md">Your Documents</Heading>
        <Button 
          leftIcon={<FiRefreshCw />} 
          size="sm" 
          onClick={fetchDocuments}
          colorScheme="blue"
          variant="outline"
        >
          Refresh
        </Button>
      </HStack>

      {documents.length === 0 ? (
        <Box p={4} borderWidth="1px" borderRadius="md" bg="gray.50">
          <Text textAlign="center">No documents found. Upload a document to get started.</Text>
        </Box>
      ) : (
        <VStack spacing={3} align="stretch">
          {documents.map((doc) => (
            <Box 
              key={doc.id || doc.filename} 
              p={3} 
              borderWidth="1px" 
              borderRadius="md"
              _hover={{ bg: 'gray.50' }}
            >
              <HStack justifyContent="space-between">
                <HStack>
                  <Icon as={FiFile} color="blue.500" boxSize={5} />
                  <VStack align="start" spacing={0}>
                    <Text fontWeight="medium">{doc.filename}</Text>
                    <Text fontSize="sm" color="gray.500">
                      {doc.metadata?.content_type || 'Document'}
                    </Text>
                  </VStack>
                </HStack>
                <HStack>
                  <Button 
                    size="sm" 
                    leftIcon={<FiDownload />} 
                    onClick={() => handleDownload(doc.filename)}
                    colorScheme="blue"
                    variant="ghost"
                  >
                    Download
                  </Button>
                  <Button 
                    size="sm" 
                    leftIcon={<FiTrash2 />} 
                    onClick={() => confirmDelete(doc)}
                    colorScheme="red"
                    variant="ghost"
                  >
                    Delete
                  </Button>
                </HStack>
              </HStack>
            </Box>
          ))}
        </VStack>
      )}

      {/* Delete Confirmation Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Confirm Delete</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            Are you sure you want to delete the document 
            <Text as="span" fontWeight="bold"> {selectedDocument?.filename}</Text>?
            This action cannot be undone.
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button colorScheme="red" onClick={handleDelete}>
              Delete
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default DocumentList;
