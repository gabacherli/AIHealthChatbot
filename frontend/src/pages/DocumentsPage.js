import { useState } from 'react';
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
  Icon,
  HStack,
} from '@chakra-ui/react';
import { FiUpload, FiFolder } from 'react-icons/fi';
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
    <Container maxW="container.xl" py={{ base: 4, md: 8 }}>
      <VStack spacing={{ base: 4, md: 6 }} align="stretch">
        {/* Header Section */}
        <Box textAlign={{ base: "center", md: "left" }}>
          <Heading as="h1" size={{ base: "lg", md: "xl" }} mb={2}>
            Document Management
          </Heading>
          <Text
            color={useColorModeValue('gray.600', 'gray.400')}
            fontSize={{ base: "sm", md: "md" }}
          >
            Upload and manage your medical documents for AI-powered health insights
          </Text>
        </Box>

        <Divider />

        {/* Tabs Section */}
        <Tabs
          variant="enclosed"
          colorScheme="blue"
          size={{ base: "sm", md: "md" }}
        >
          <TabList>
            <Tab>
              <HStack spacing={2}>
                <Icon as={FiFolder} boxSize={4} />
                <Text>My Documents</Text>
              </HStack>
            </Tab>
            <Tab>
              <HStack spacing={2}>
                <Icon as={FiUpload} boxSize={4} />
                <Text>Upload New</Text>
              </HStack>
            </Tab>
          </TabList>

          <TabPanels>
            <TabPanel
              bg={bgColor}
              borderWidth="1px"
              borderTop="none"
              borderColor={borderColor}
              borderBottomRadius="md"
              p={{ base: 4, md: 6 }}
            >
              <DocumentList
                key={refreshKey}
                onDocumentDeleted={handleDocumentDeleted}
              />
            </TabPanel>
            <TabPanel
              bg={bgColor}
              borderWidth="1px"
              borderTop="none"
              borderColor={borderColor}
              borderBottomRadius="md"
              p={{ base: 4, md: 6 }}
            >
              <DocumentUpload onUploadSuccess={handleUploadSuccess} />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Container>
  );
};

export default DocumentsPage;
