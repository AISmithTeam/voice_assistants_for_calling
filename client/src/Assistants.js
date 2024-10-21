import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Heading,
  Select,
  Textarea,
  VStack,
  HStack,
  Text,
  Grid,
  GridItem,
  Flex,
  Tooltip,
  Container,
} from '@chakra-ui/react';
import { InfoIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons';

const Assistants = () => {
  const [systemPrompt, setSystemPrompt] = useState('');
  const [voice, setVoice] = useState('');
  const [assistants, setAssistants] = useState([]);
  // edit to post to assistants endpoint
  const handleSubmit = (e) => {
    e.preventDefault();
    const newAssistant = { systemPrompt, voice };
    setAssistants([...assistants, newAssistant]);
    setSystemPrompt('');
    setVoice('');
  };

  return (
    <Container maxW="container.xl" py={6}>
      <Heading mb={6} fontSize={{ base: "2xl", md: "3xl" }} textAlign="left">Assistants Management</Heading>
      <Grid templateColumns={{ base: "1fr", lg: "3fr 2fr" }} gap={8}>
        <GridItem>
          <VStack spacing={4} align="stretch" as="form" onSubmit={handleSubmit} bg="white" p={6} borderRadius="md" boxShadow="sm">
            <FormControl isRequired>
              <Flex align="center" mb={2}>
                <FormLabel mb={0} fontSize="md">System Prompt</FormLabel>
                <Tooltip label="Enter the system prompt for the assistant" placement="top-start">
                  <InfoIcon ml={2} fontSize="sm" />
                </Tooltip>
              </Flex>
              <Textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                placeholder="Enter system prompt here..."
                minHeight="150px"
                resize="vertical"
                fontSize="sm"
              />
            </FormControl>
            <FormControl isRequired>
              <Flex align="center" mb={2}>
                <FormLabel mb={0} fontSize="md">Voice Selection</FormLabel>
                <Tooltip label="Choose the voice for the assistant" placement="top-start">
                  <InfoIcon ml={2} fontSize="sm" />
                </Tooltip>
              </Flex>
              <Select value={voice} onChange={(e) => setVoice(e.target.value)} fontSize="sm">
                <option value="">Select a voice</option>
                <option value="voice1">Voice 1</option>
                <option value="voice2">Voice 2</option>
                <option value="voice3">Voice 3</option>
              </Select>
            </FormControl>
            <Button type="submit" colorScheme="blue" size="md">Create Assistant</Button>
          </VStack>
        </GridItem>

        <GridItem>
          <Box bg="gray.50" p={6} borderRadius="md" boxShadow="sm" height="100%">
            <Heading size="md" mb={4} textAlign="left">Existing Assistants</Heading>
            {assistants.length > 0 ? (
              <VStack spacing={4} align="stretch">
                {assistants.map((assistant, index) => (
                  <Box key={index} borderWidth={1} borderRadius="md" p={4} bg="white">
                    <Text fontSize="sm"><strong>System Prompt:</strong> {assistant.systemPrompt.substring(0, 50)}...</Text>
                    <Text fontSize="sm" mt={2}><strong>Voice:</strong> {assistant.voice}</Text>
                    <HStack spacing={2} mt={3}>
                      <Button leftIcon={<EditIcon />} colorScheme="blue" size="sm">Edit</Button>
                      <Button leftIcon={<DeleteIcon />} colorScheme="red" size="sm">Delete</Button>
                    </HStack>
                  </Box>
                ))}
              </VStack>
            ) : (
              <Text fontSize="sm">No assistants created yet.</Text>
            )}
          </Box>
        </GridItem>
      </Grid>
    </Container>
  );
};

export default Assistants;
