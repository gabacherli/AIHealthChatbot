import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Card,
  CardBody,
  CardHeader,
  SimpleGrid,
  Badge,
  Button,
  Icon,
  Flex,
  Spacer,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Divider,
  List,
  ListItem,
  ListIcon
} from '@chakra-ui/react';
import { 
  FiUsers, 
  FiFileText, 
  FiShield, 
  FiEye, 
  FiCalendar, 
  FiUser,
  FiCheck,
  FiX,
  FiClock
} from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';
import { relationshipService, documentService } from '../services/api';

const PatientDashboard = () => {
  const { user } = useAuth();
  const [professionals, setProfessionals] = useState([]);
  const [sharedDocuments, setSharedDocuments] = useState([]);
  const [accessSummary, setAccessSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { isOpen: isAccessOpen, onOpen: onAccessOpen, onClose: onAccessClose } = useDisclosure();

  // Color mode values
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');
  const textSecondary = useColorModeValue('gray.600', 'gray.400');
  const badgeColorScheme = {
    active: 'green',
    pending: 'yellow',
    inactive: 'gray',
    terminated: 'red'
  };

  useEffect(() => {
    if (user && user.role === 'patient') {
      loadPatientData();
    }
  }, [user]);

  const loadPatientData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get patient's healthcare professionals
      const professionalsResponse = await relationshipService.getPatientProfessionals(user.id);
      setProfessionals(professionalsResponse.relationships || []);

      // Get patient's shared documents
      const documentsResponse = await documentService.getPatientSharedDocuments(user.id);
      setSharedDocuments(documentsResponse.documents || []);

      // Get access summary
      const summaryResponse = await documentService.getPatientAccessSummary(user.id);
      setAccessSummary(summaryResponse);

    } catch (err) {
      console.error('Error loading patient data:', err);
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getActiveProfessionals = () => {
    return professionals.filter(rel => rel.relationship_status === 'active');
  };

  const getSharedDocumentsCount = () => {
    return sharedDocuments.filter(doc => doc.is_shared).length;
  };

  if (user?.role !== 'patient') {
    return (
      <Alert status="error">
        <AlertIcon />
        Access denied. This dashboard is only available to patients.
      </Alert>
    );
  }

  if (loading) {
    return (
      <Flex justify="center" align="center" minH="400px">
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text>Loading dashboard...</Text>
        </VStack>
      </Flex>
    );
  }

  return (
    <Box p={6} maxW="1400px" mx="auto">
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>Patient Dashboard</Heading>
          <Text color={textSecondary}>
            Welcome back, {user.full_name || user.username}
          </Text>
        </Box>

        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}

        {/* Summary Cards */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
            <CardBody>
              <HStack spacing={4}>
                <Icon as={FiUsers} boxSize={8} color="blue.500" />
                <Box>
                  <Text fontSize="2xl" fontWeight="bold">{getActiveProfessionals().length}</Text>
                  <Text color={textSecondary} fontSize="sm">Healthcare Professionals</Text>
                </Box>
              </HStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
            <CardBody>
              <HStack spacing={4}>
                <Icon as={FiFileText} boxSize={8} color="green.500" />
                <Box>
                  <Text fontSize="2xl" fontWeight="bold">{sharedDocuments.length}</Text>
                  <Text color={textSecondary} fontSize="sm">Total Documents</Text>
                </Box>
              </HStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
            <CardBody>
              <HStack spacing={4}>
                <Icon as={FiShield} boxSize={8} color="purple.500" />
                <Box>
                  <Text fontSize="2xl" fontWeight="bold">{getSharedDocumentsCount()}</Text>
                  <Text color={textSecondary} fontSize="sm">Shared Documents</Text>
                </Box>
              </HStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Main Content Tabs */}
        <Tabs variant="enclosed" colorScheme="blue">
          <TabList>
            <Tab>My Healthcare Team</Tab>
            <Tab>Document Sharing</Tab>
            <Tab>Privacy & Access</Tab>
          </TabList>

          <TabPanels>
            {/* Healthcare Team Tab */}
            <TabPanel px={0}>
              <VStack spacing={6} align="stretch">
                <Flex justify="space-between" align="center">
                  <Heading size="md">My Healthcare Professionals</Heading>
                  <Button colorScheme="blue" onClick={loadPatientData}>
                    Refresh
                  </Button>
                </Flex>

                {professionals.length === 0 ? (
                  <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
                    <CardBody>
                      <VStack spacing={4} py={8}>
                        <Icon as={FiUsers} boxSize={12} color={textSecondary} />
                        <Text color={textSecondary}>No healthcare professionals assigned yet</Text>
                        <Text fontSize="sm" color={textSecondary} textAlign="center">
                          Contact your healthcare provider to establish a professional relationship
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>
                ) : (
                  <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                    {professionals.map((relationship) => {
                      const professional = relationship.professional;
                      
                      return (
                        <Card
                          key={relationship.id}
                          bg={cardBg}
                          borderColor={cardBorder}
                          borderWidth="1px"
                          _hover={{ shadow: 'md' }}
                        >
                          <CardHeader pb={2}>
                            <Flex align="center">
                              <HStack spacing={3} flex={1}>
                                <Icon as={FiUser} boxSize={5} color="blue.500" />
                                <Box>
                                  <Text fontWeight="semibold">{professional.full_name}</Text>
                                  <Text fontSize="sm" color={textSecondary}>
                                    {professional.specialty || 'Healthcare Professional'}
                                  </Text>
                                </Box>
                              </HStack>
                              <Badge colorScheme={badgeColorScheme[relationship.relationship_status]}>
                                {relationship.relationship_status}
                              </Badge>
                            </Flex>
                          </CardHeader>
                          <CardBody pt={0}>
                            <VStack spacing={3} align="stretch">
                              <HStack justify="space-between">
                                <Text fontSize="sm" color={textSecondary}>Relationship:</Text>
                                <Text fontSize="sm" fontWeight="medium">
                                  {relationship.relationship_type.replace('_', ' ')}
                                </Text>
                              </HStack>
                              
                              {professional.organization && (
                                <HStack justify="space-between">
                                  <Text fontSize="sm" color={textSecondary}>Organization:</Text>
                                  <Text fontSize="sm">{professional.organization}</Text>
                                </HStack>
                              )}

                              <Divider />
                              
                              <Box>
                                <Text fontSize="sm" color={textSecondary} mb={2}>Permissions:</Text>
                                <VStack spacing={1} align="stretch">
                                  <HStack>
                                    <Icon 
                                      as={relationship.can_view_documents ? FiCheck : FiX} 
                                      color={relationship.can_view_documents ? 'green.500' : 'red.500'}
                                      boxSize={4}
                                    />
                                    <Text fontSize="sm">View Documents</Text>
                                  </HStack>
                                  <HStack>
                                    <Icon 
                                      as={relationship.can_add_notes ? FiCheck : FiX} 
                                      color={relationship.can_add_notes ? 'green.500' : 'red.500'}
                                      boxSize={4}
                                    />
                                    <Text fontSize="sm">Add Notes</Text>
                                  </HStack>
                                  <HStack>
                                    <Icon 
                                      as={relationship.can_request_tests ? FiCheck : FiX} 
                                      color={relationship.can_request_tests ? 'green.500' : 'red.500'}
                                      boxSize={4}
                                    />
                                    <Text fontSize="sm">Request Tests</Text>
                                  </HStack>
                                </VStack>
                              </Box>

                              {relationship.notes && (
                                <Box>
                                  <Text fontSize="sm" color={textSecondary} mb={1}>Notes:</Text>
                                  <Text fontSize="sm" noOfLines={2}>{relationship.notes}</Text>
                                </Box>
                              )}
                            </VStack>
                          </CardBody>
                        </Card>
                      );
                    })}
                  </SimpleGrid>
                )}
              </VStack>
            </TabPanel>

            {/* Document Sharing Tab */}
            <TabPanel px={0}>
              <VStack spacing={6} align="stretch">
                <Flex justify="space-between" align="center">
                  <Heading size="md">Document Sharing Status</Heading>
                  <Button colorScheme="blue" onClick={loadPatientData}>
                    Refresh
                  </Button>
                </Flex>

                {sharedDocuments.length === 0 ? (
                  <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
                    <CardBody>
                      <VStack spacing={4} py={8}>
                        <Icon as={FiFileText} boxSize={12} color={textSecondary} />
                        <Text color={textSecondary}>No documents uploaded yet</Text>
                        <Text fontSize="sm" color={textSecondary} textAlign="center">
                          Upload documents to share them with your healthcare team
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>
                ) : (
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                    {sharedDocuments.map((doc) => (
                      <Card
                        key={doc.document_id}
                        bg={cardBg}
                        borderColor={cardBorder}
                        borderWidth="1px"
                        _hover={{ shadow: 'md' }}
                      >
                        <CardBody>
                          <VStack spacing={4} align="stretch">
                            <HStack justify="space-between">
                              <Text fontWeight="semibold" noOfLines={2} flex={1}>
                                {doc.filename}
                              </Text>
                              <Badge colorScheme={doc.is_shared ? 'green' : 'gray'}>
                                {doc.is_shared ? 'Shared' : 'Private'}
                              </Badge>
                            </HStack>

                            <HStack justify="space-between">
                              <Text fontSize="sm" color={textSecondary}>Type:</Text>
                              <Text fontSize="sm">{doc.content_type}</Text>
                            </HStack>

                            {doc.upload_date && (
                              <HStack justify="space-between">
                                <Text fontSize="sm" color={textSecondary}>Uploaded:</Text>
                                <Text fontSize="sm">
                                  {new Date(doc.upload_date).toLocaleDateString()}
                                </Text>
                              </HStack>
                            )}

                            <HStack justify="space-between">
                              <Text fontSize="sm" color={textSecondary}>Shared with:</Text>
                              <Text fontSize="sm" fontWeight="medium">
                                {doc.shared_with_count} professionals
                              </Text>
                            </HStack>

                            {doc.shared_with_professionals && doc.shared_with_professionals.length > 0 && (
                              <Box>
                                <Text fontSize="sm" color={textSecondary} mb={2}>
                                  Accessible by:
                                </Text>
                                <VStack spacing={1} align="stretch">
                                  {doc.shared_with_professionals.slice(0, 3).map((prof) => (
                                    <Text key={prof.professional_id} fontSize="sm">
                                      • {prof.professional_name} ({prof.relationship_type.replace('_', ' ')})
                                    </Text>
                                  ))}
                                  {doc.shared_with_professionals.length > 3 && (
                                    <Text fontSize="sm" color={textSecondary}>
                                      ... and {doc.shared_with_professionals.length - 3} more
                                    </Text>
                                  )}
                                </VStack>
                              </Box>
                            )}
                          </VStack>
                        </CardBody>
                      </Card>
                    ))}
                  </SimpleGrid>
                )}
              </VStack>
            </TabPanel>

            {/* Privacy & Access Tab */}
            <TabPanel px={0}>
              <VStack spacing={6} align="stretch">
                <Flex justify="space-between" align="center">
                  <Heading size="md">Privacy & Access Control</Heading>
                  <Button colorScheme="blue" onClick={onAccessOpen}>
                    View Access Log
                  </Button>
                </Flex>

                <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
                  <CardHeader>
                    <Text fontWeight="semibold">Data Sharing Summary</Text>
                  </CardHeader>
                  <CardBody pt={0}>
                    <VStack spacing={4} align="stretch">
                      <HStack justify="space-between">
                        <Text>Total Healthcare Professionals:</Text>
                        <Text fontWeight="medium">{professionals.length}</Text>
                      </HStack>
                      <HStack justify="space-between">
                        <Text>Active Relationships:</Text>
                        <Text fontWeight="medium">{getActiveProfessionals().length}</Text>
                      </HStack>
                      <HStack justify="space-between">
                        <Text>Documents Shared:</Text>
                        <Text fontWeight="medium">{getSharedDocumentsCount()}</Text>
                      </HStack>
                      <HStack justify="space-between">
                        <Text>Total Documents:</Text>
                        <Text fontWeight="medium">{sharedDocuments.length}</Text>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>

                <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
                  <CardHeader>
                    <Text fontWeight="semibold">Your Rights</Text>
                  </CardHeader>
                  <CardBody pt={0}>
                    <List spacing={3}>
                      <ListItem>
                        <ListIcon as={FiCheck} color="green.500" />
                        You control who has access to your medical documents
                      </ListItem>
                      <ListItem>
                        <ListIcon as={FiCheck} color="green.500" />
                        You can view who has accessed your data and when
                      </ListItem>
                      <ListItem>
                        <ListIcon as={FiCheck} color="green.500" />
                        You can request termination of professional relationships
                      </ListItem>
                      <ListItem>
                        <ListIcon as={FiCheck} color="green.500" />
                        All access to your data is logged for your security
                      </ListItem>
                    </List>
                  </CardBody>
                </Card>
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>

      {/* Access Log Modal */}
      <Modal isOpen={isAccessOpen} onClose={onAccessClose} size="xl">
        <ModalOverlay bg="blackAlpha.600" />
        <ModalContent borderRadius="3xl" border="2px solid" borderColor={cardBorder}>
          <ModalHeader>Access Log</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {accessSummary ? (
              <VStack spacing={4} align="stretch">
                <Text fontSize="sm" color={textSecondary}>
                  Last 30 days of access activity
                </Text>
                
                <Box>
                  <Text fontWeight="semibold" mb={2}>Summary</Text>
                  <VStack spacing={2} align="stretch">
                    <HStack justify="space-between">
                      <Text fontSize="sm">Total Access Events:</Text>
                      <Text fontSize="sm" fontWeight="medium">
                        {accessSummary.total_access_events}
                      </Text>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm">Unique Professionals:</Text>
                      <Text fontSize="sm" fontWeight="medium">
                        {accessSummary.unique_professionals}
                      </Text>
                    </HStack>
                  </VStack>
                </Box>

                {Object.keys(accessSummary.professional_access || {}).length > 0 && (
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Professional Access</Text>
                    <VStack spacing={2} align="stretch">
                      {Object.entries(accessSummary.professional_access).map(([name, data]) => (
                        <HStack key={name} justify="space-between">
                          <Text fontSize="sm">{name}:</Text>
                          <Text fontSize="sm" fontWeight="medium">
                            {data.access_count} accesses
                          </Text>
                        </HStack>
                      ))}
                    </VStack>
                  </Box>
                )}
              </VStack>
            ) : (
              <Text color={textSecondary}>Loading access summary...</Text>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default PatientDashboard;
