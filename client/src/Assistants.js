import React, { useState, useEffect } from 'react';
import axios from "axios";
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
  Input,
  Alert,
  AlertIcon,
  Progress,
  Grid,
  GridItem,
  Flex,
  Tooltip,
  Container,
} from '@chakra-ui/react';
import { InfoIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons';


const Assistants = () => {
  const base_url = '127.0.0.1:5000';
  const access_token = localStorage.getItem("access_token");
  const [systemPrompt, setSystemPrompt] = useState('');
  const [voice, setVoice] = useState('');
  const [assistant_id, setAssistantId] = useState(0);
  const [assistants, setAssistants] = useState([]);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileContent, setFileContent] = useState("");
  const [fileName, setFileName] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadedFile, setUploadedFile] = useState(null);

  useEffect(() => {
    const url = `http://${base_url}/assistants?jwt_token=${access_token}`;
    axios
      .get(url)
      .then(function (response) {
        const data = response.data;
        var user_assistants = [];
        var assistant_id, systemPrompt, voice;
        for (var i=0; i < data.length; i++) {
          assistant_id = data[i].assistant_id;
          systemPrompt = data[i].prompt;
          voice = data[i].voice;
          user_assistants.push( { systemPrompt, voice, assistant_id } );
        }
        setAssistants(user_assistants);
      });
    }, []);

    /*const handleFileUpload = (e) => {
      for (let i = 0; i < e.target.files.length; i++) {
        const file = e.target.files[i];
        if (file) {
          setFileName(file.name);
          setUploadedFile(file);
          setUploadedFiles([...uploadedFiles, file]);
          setUploadStatus('uploading');
          let progress = 0;
          const interval = setInterval(() => {
            progress += 10;
            setUploadProgress(progress);
            if (progress >= 100) {
              clearInterval(interval);
              setUploadStatus('success');
            }
          }, 200);
        } else {
          setUploadStatus('error');
          setUploadedFile(null);
          e.target.value = null;
        }
      }
      console.log(uploadedFiles);
    };*/

  // edit to post to assistants endpoint
  const handleSubmit = (e) => {
    e.preventDefault();
    const newAssistant = { systemPrompt, voice, assistant_id };
    setAssistants([...assistants, newAssistant]);
    //setSystemPrompt('');
    //setVoice('');

    axios
      .post(`http://${base_url}/assistants?jwt_token=${access_token}`, {
        prompt: systemPrompt,
        voice: voice
      })
      .then(function (response) {
        setSystemPrompt(response.prompt);
        setVoice(response.voice);
        setAssistantId(response.id);
      });

    setAssistantId(assistant_id);
    setAssistants([...assistants, newAssistant]);
  };

  return (
    <Container maxW="container.xl" py={6} style={{position: 'absolute', width: "80%"}}>
      <Heading mb={6} fontSize={{ base: "2xl", md: "3xl" }} textAlign="left">Assistants Management</Heading>
      <VStack spacing={4} align="stretch">
          <VStack spacing={4} align="center" width="70%" as="form" onSubmit={handleSubmit} bg="white" p={6} borderRadius="md" boxShadow="sm">
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
                <option value="alloy">Alloy</option>
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel mb={1}>
                Upload File
                <Tooltip label="Upload a file containing additional campaign data" placement="top-start">
                  <InfoIcon ml={2} />
                </Tooltip>
              </FormLabel>
            </FormControl>
            <Button type="submit" colorScheme="blue" size="md">Create Assistant</Button>
          </VStack>

          <Box bg="gray.50" p={6} borderRadius="md" boxShadow="sm" height="100%" width="70%">
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
      </VStack>
    </Container>
  );
};

export default Assistants;
