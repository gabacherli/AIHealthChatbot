import React, { useState, useEffect } from 'react';
import {
  Box,
  Select,
  FormControl,
  FormLabel,
  Text,
  HStack,
  Icon,
  Badge,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import { FiUser, FiUsers } from 'react-icons/fi';
import chatService from '../services/chatService';

/**
 * Patient selector component for healthcare professionals
 */
const PatientSelector = ({ selectedPatientId, onPatientChange, disabled = false }) => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Color mode values
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textSecondary = useColorModeValue('gray.600', 'gray.400');

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await chatService.getAvailablePatients();
      setPatients(response.patients || []);
    } catch (err) {
      console.error('Error loading patients:', err);
      setError(err.message || 'Failed to load patients');
    } finally {
      setLoading(false);
    }
  };

  const handlePatientChange = (event) => {
    const patientId = event.target.value;
    const selectedPatient = patients.find(p => p.id.toString() === patientId);
    onPatientChange(patientId ? parseInt(patientId) : null, selectedPatient);
  };

  const getSelectedPatient = () => {
    return patients.find(p => p.id === selectedPatientId);
  };

  if (loading) {
    return (
      <Box p={4} bg={bgColor} borderWidth="1px" borderColor={borderColor} borderRadius="md">
        <HStack spacing={3}>
          <Spinner size="sm" />
          <Text fontSize="sm" color={textSecondary}>Loading patients...</Text>
        </HStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        <Text fontSize="sm">{error}</Text>
      </Alert>
    );
  }

  return (
    <Box p={4} bg={bgColor} borderWidth="1px" borderColor={borderColor} borderRadius="md">
      <FormControl>
        <FormLabel fontSize="sm" fontWeight="semibold" mb={2}>
          <HStack spacing={2}>
            <Icon as={FiUsers} />
            <Text>Select Patient for Context</Text>
          </HStack>
        </FormLabel>
        
        <Select
          placeholder="Choose a patient or leave blank for general consultation"
          value={selectedPatientId || ''}
          onChange={handlePatientChange}
          disabled={disabled}
          size="sm"
        >
          {patients.map((patient) => (
            <option key={patient.id} value={patient.id}>
              {patient.full_name} (@{patient.username})
            </option>
          ))}
        </Select>

        {/* Selected patient info */}
        {selectedPatientId && (
          <Box mt={3} p={3} bg={useColorModeValue('blue.50', 'blue.900')} borderRadius="md">
            <HStack spacing={3}>
              <Icon as={FiUser} color="blue.500" />
              <Box flex={1}>
                <Text fontSize="sm" fontWeight="medium">
                  {getSelectedPatient()?.full_name}
                </Text>
                <HStack spacing={2} mt={1}>
                  <Text fontSize="xs" color={textSecondary}>
                    @{getSelectedPatient()?.username}
                  </Text>
                  <Badge size="sm" colorScheme="blue">
                    {getSelectedPatient()?.relationship_type}
                  </Badge>
                  {getSelectedPatient()?.can_view_documents && (
                    <Badge size="sm" colorScheme="green">
                      Document Access
                    </Badge>
                  )}
                </HStack>
              </Box>
            </HStack>
          </Box>
        )}

        {/* Patient count info */}
        <Text fontSize="xs" color={textSecondary} mt={2}>
          {patients.length === 0 
            ? 'No patients assigned' 
            : `${patients.length} patient${patients.length !== 1 ? 's' : ''} available`
          }
        </Text>
      </FormControl>
    </Box>
  );
};

export default PatientSelector;
