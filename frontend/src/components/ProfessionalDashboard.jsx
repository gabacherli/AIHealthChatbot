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
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  Divider
} from '@chakra-ui/react';
import { FiUsers, FiFileText, FiSearch, FiCalendar, FiUser } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';
import { relationshipService, documentService } from '../services/api';

const ProfessionalDashboard = () => {
  const { user } = useAuth();
  const [patients, setPatients] = useState([]);
  const [patientDocuments, setPatientDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('active');
  const [selectedPatient, setSelectedPatient] = useState(null);

  // Color mode values
  const cardBg = useColorModeValue('white', 'gray.800');
  const cardBorder = useColorModeValue('gray.200', 'gray.600');
  const textSecondary = useColorModeValue('gray.600', 'gray.400');
  const documentItemBg = useColorModeValue('gray.50', 'gray.700');
  const badgeColorScheme = {
    active: 'green',
    pending: 'yellow',
    inactive: 'gray',
    terminated: 'red'
  };

  useEffect(() => {
    if (user && user.role === 'professional') {
      loadProfessionalData();
    }
  }, [user]);

  const loadProfessionalData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get professional's patients
      const patientsResponse = await relationshipService.getProfessionalPatients(user.id, statusFilter);
      setPatients(patientsResponse.relationships || []);

      // Get all patient documents accessible to this professional
      const documentsResponse = await documentService.getProfessionalPatientDocuments(user.id);
      setPatientDocuments(documentsResponse.documents_by_patient || []);

    } catch (err) {
      console.error('Error loading professional data:', err);
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handlePatientSelect = (patient) => {
    setSelectedPatient(patient);
  };

  const filteredPatients = patients.filter(relationship => {
    const patient = relationship.patient;
    if (!patient) return false;

    const matchesSearch = !searchTerm ||
      patient.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.email?.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesSearch;
  });

  const getPatientDocuments = (patientId) => {
    const patientData = patientDocuments.find(p => p.patient_id === patientId);
    return patientData ? patientData.documents : [];
  };

  const getTotalDocumentsCount = () => {
    return patientDocuments.reduce((total, patient) => total + patient.documents.length, 0);
  };

  if (user?.role !== 'professional') {
    return (
      <Alert status="error">
        <AlertIcon />
        Access denied. This dashboard is only available to healthcare professionals.
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
      {/* Header */}
      <VStack spacing={6} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>Professional Dashboard</Heading>
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
                  <Text fontSize="2xl" fontWeight="bold">{patients.length}</Text>
                  <Text color={textSecondary} fontSize="sm">Active Patients</Text>
                </Box>
              </HStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
            <CardBody>
              <HStack spacing={4}>
                <Icon as={FiFileText} boxSize={8} color="green.500" />
                <Box>
                  <Text fontSize="2xl" fontWeight="bold">{getTotalDocumentsCount()}</Text>
                  <Text color={textSecondary} fontSize="sm">Accessible Documents</Text>
                </Box>
              </HStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
            <CardBody>
              <HStack spacing={4}>
                <Icon as={FiCalendar} boxSize={8} color="purple.500" />
                <Box>
                  <Text fontSize="2xl" fontWeight="bold">{patientDocuments.length}</Text>
                  <Text color={textSecondary} fontSize="sm">Patients with Documents</Text>
                </Box>
              </HStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Main Content Tabs */}
        <Tabs variant="enclosed" colorScheme="blue">
          <TabList>
            <Tab>My Patients</Tab>
            <Tab>Patient Documents</Tab>
          </TabList>

          <TabPanels>
            {/* Patients Tab */}
            <TabPanel px={0}>
              <VStack spacing={6} align="stretch">
                {/* Search and Filters */}
                <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
                  <CardBody>
                    <HStack spacing={4}>
                      <InputGroup flex={1}>
                        <InputLeftElement>
                          <Icon as={FiSearch} color={textSecondary} />
                        </InputLeftElement>
                        <Input
                          placeholder="Search patients by name, username, or email..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                        />
                      </InputGroup>
                      <Select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        maxW="200px"
                      >
                        <option value="active">Active</option>
                        <option value="pending">Pending</option>
                        <option value="inactive">Inactive</option>
                        <option value="terminated">Terminated</option>
                      </Select>
                      <Button onClick={loadProfessionalData} colorScheme="blue">
                        Refresh
                      </Button>
                    </HStack>
                  </CardBody>
                </Card>

                {/* Patients List */}
                {filteredPatients.length === 0 ? (
                  <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
                    <CardBody>
                      <VStack spacing={4} py={8}>
                        <Icon as={FiUsers} boxSize={12} color={textSecondary} />
                        <Text color={textSecondary}>
                          {patients.length === 0 ? 'No patients assigned yet' : 'No patients match your search criteria'}
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>
                ) : (
                  <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                    {filteredPatients.map((relationship) => {
                      const patient = relationship.patient;
                      const documentCount = getPatientDocuments(patient.id).length;

                      return (
                        <Card
                          key={relationship.id}
                          bg={cardBg}
                          borderColor={cardBorder}
                          borderWidth="1px"
                          _hover={{ shadow: 'md', borderColor: 'blue.300' }}
                          cursor="pointer"
                          onClick={() => handlePatientSelect(patient)}
                        >
                          <CardHeader pb={2}>
                            <Flex align="center">
                              <HStack spacing={3} flex={1}>
                                <Icon as={FiUser} boxSize={5} color="blue.500" />
                                <Box>
                                  <Text fontWeight="semibold">{patient.full_name}</Text>
                                  <Text fontSize="sm" color={textSecondary}>@{patient.username}</Text>
                                </Box>
                              </HStack>
                              <Badge colorScheme={badgeColorScheme[relationship.relationship_status]}>
                                {relationship.relationship_status}
                              </Badge>
                            </Flex>
                          </CardHeader>
                          <CardBody pt={0}>
                            <VStack spacing={2} align="stretch">
                              <HStack justify="space-between">
                                <Text fontSize="sm" color={textSecondary}>Relationship:</Text>
                                <Text fontSize="sm" fontWeight="medium">
                                  {relationship.relationship_type.replace('_', ' ')}
                                </Text>
                              </HStack>
                              <HStack justify="space-between">
                                <Text fontSize="sm" color={textSecondary}>Documents:</Text>
                                <Text fontSize="sm" fontWeight="medium">{documentCount}</Text>
                              </HStack>
                              {patient.email && (
                                <HStack justify="space-between">
                                  <Text fontSize="sm" color={textSecondary}>Email:</Text>
                                  <Text fontSize="sm">{patient.email}</Text>
                                </HStack>
                              )}
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

            {/* Patient Documents Tab */}
            <TabPanel px={0}>
              <VStack spacing={6} align="stretch">
                {patientDocuments.length === 0 ? (
                  <Card bg={cardBg} borderColor={cardBorder} borderWidth="1px">
                    <CardBody>
                      <VStack spacing={4} py={8}>
                        <Icon as={FiFileText} boxSize={12} color={textSecondary} />
                        <Text color={textSecondary}>No patient documents available</Text>
                      </VStack>
                    </CardBody>
                  </Card>
                ) : (
                  patientDocuments.map((patientData) => (
                    <Card key={patientData.patient_id} bg={cardBg} borderColor={cardBorder} borderWidth="1px">
                      <CardHeader>
                        <HStack>
                          <Icon as={FiUser} color="blue.500" />
                          <Text fontWeight="semibold">{patientData.patient_name}</Text>
                          <Spacer />
                          <Badge colorScheme="blue">{patientData.documents.length} documents</Badge>
                        </HStack>
                      </CardHeader>
                      <CardBody pt={0}>
                        {patientData.documents.length === 0 ? (
                          <Text color={textSecondary} fontSize="sm">No documents uploaded</Text>
                        ) : (
                          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                            {patientData.documents.map((doc) => (
                              <Box
                                key={doc.document_id}
                                p={4}
                                borderWidth="1px"
                                borderColor={cardBorder}
                                borderRadius="md"
                                _hover={{ bg: documentItemBg }}
                              >
                                <VStack spacing={2} align="stretch">
                                  <Text fontWeight="medium" fontSize="sm" noOfLines={2}>
                                    {doc.filename}
                                  </Text>
                                  <Text fontSize="xs" color={textSecondary}>
                                    {doc.content_type}
                                  </Text>
                                  {doc.upload_date && (
                                    <Text fontSize="xs" color={textSecondary}>
                                      {new Date(doc.upload_date).toLocaleDateString()}
                                    </Text>
                                  )}
                                  <Button size="xs" colorScheme="blue" variant="outline">
                                    View Document
                                  </Button>
                                </VStack>
                              </Box>
                            ))}
                          </SimpleGrid>
                        )}
                      </CardBody>
                    </Card>
                  ))
                )}
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </VStack>
    </Box>
  );
};

export default ProfessionalDashboard;
