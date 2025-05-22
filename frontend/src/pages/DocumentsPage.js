import React, { useState } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Divider,
  useColorModeValue,
  VStack,
} from '@chakra-ui/react';
import DocumentUpload from '../components/DocumentUpload';
import DocumentList from '../components/DocumentList';

const DocumentsPage = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  const handleUploadSuccess = () => {
    // Trigger a refresh of the document list
    setRefreshKey(prevKey => prevKey + 1);
  };

  const handleDocumentDeleted = () => {
    // No need to do anything here as the DocumentList component
    // handles the removal internally
  };

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading as="h1" size="xl">Document Management</Heading>
          <Text mt={2} color="gray.600">
            Upload and manage your medical documents for better health insights
          </Text>
        </Box>

        <Divider />

        <Tabs variant="enclosed" colorScheme="blue">
          <TabList>
            <Tab>My Documents</Tab>
            <Tab>Upload New</Tab>
          </TabList>
          <TabPanels>
            <TabPanel bg={bgColor} borderWidth="1px" borderTop="none" borderColor={borderColor} borderBottomRadius="md">
              <DocumentList 
                key={refreshKey} 
                onDocumentDeleted={handleDocumentDeleted} 
              />
            </TabPanel>
            <TabPanel bg={bgColor} borderWidth="1px" borderTop="none" borderColor={borderColor} borderBottomRadius="md">
              <DocumentUpload onUploadSuccess={handleUploadSuccess} />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Container>
  );
};

export default DocumentsPage;
