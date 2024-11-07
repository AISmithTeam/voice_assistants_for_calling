import React, { useState, useEffect, useMemo } from 'react';
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
  Flex,
  Tooltip,
  Container,
  Input,
} from '@chakra-ui/react';
import { InfoIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons';
import { useDropzone } from "react-dropzone"


const Assistants = () => {
  const base_url = '127.0.0.1:5000';
  const access_token = localStorage.getItem("access_token");
  const [systemPrompt, setSystemPrompt] = useState('');
  const [voice, setVoice] = useState('');
  const [assistant_id, setAssistantId] = useState(0);
  const [assistants, setAssistants] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [assistantName, setAssistantName] = useState('');

  const baseStyle = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    width: '768px',
    padding: '20px',
    borderWidth: 2,
    borderRadius: 2,
    borderColor: '#eeeeee',
    borderStyle: 'dashed',
    backgroundColor: '#fafafa',
    color: '#bdbdbd',
    outline: 'none',
    transition: 'border .24s ease-in-out'
  };
  
  const focusedStyle = {
    borderColor: '#2196f3'
  };
  
  const acceptStyle = {
    borderColor: '#00e676'
  };
  
  const rejectStyle = {
    borderColor: '#ff1744'
  };
  
  function StyledDropzone(props, onDrop) {
    const {
      getRootProps,
      getInputProps,
      isFocused,
      isDragAccept,
      isDragReject
    } = useDropzone({onDrop: (incomingFiles) => {handleFileUpload(incomingFiles)}});
  
    const style = useMemo(() => ({
      ...baseStyle,
      ...(isFocused ? focusedStyle : {}),
      ...(isDragAccept ? acceptStyle : {}),
      ...(isDragReject ? rejectStyle : {})
    }), [
      isFocused,
      isDragAccept,
      isDragReject
    ]);

    const files = uploadedFiles.map(file => (
      <li key={file.name}>
        {file.name} - {file.size} bytes
      </li>
    ));

    return (
      <div className="container">
        <div {...getRootProps({style})}>
          <input {...getInputProps()} />
          <p>Drop files here, or click to select files</p>
          <aside>
            <ul>{files}</ul>
          </aside>
        </div>
        
      </div>
    );
  }

  useEffect(() => {
    const url = `http://${base_url}/assistants?jwt_token=${access_token}`;
    axios
      .get(url)
      .then(function (response) {
        const data = response.data;
        var user_assistants = [];
        var assistant_id, systemPrompt, voice, assistantName;
        console.log(data);
        for (var i=0; i < data.length; i++) {
          assistantName = data[i].assistant_name;
          assistant_id = data[i].id;
          systemPrompt = data[i].prompt;
          voice = data[i].voice;
          user_assistants.push( { systemPrompt, voice, assistantName, assistant_id } );
        }
        console.log(user_assistants);
        setAssistants(user_assistants);
      });
    }, [access_token]);

    const handleFileUpload = async (files) => {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        console.log(file);
        if (file) {
          setUploadedFiles([...uploadedFiles, file]);
        }
      }
    };

  // edit to post to assistants endpoint
  const handleSubmit = (e) => {
    e.preventDefault();
    const newAssistant = { systemPrompt, voice, assistantName, assistant_id };
    setAssistants([...assistants, newAssistant]);
    //setSystemPrompt('');
    //setVoice('');

    axios
      .post(`http://${base_url}/assistants?jwt_token=${access_token}`, {
        prompt: systemPrompt,
        voice: voice,
        assistant_name: assistantName
      })
      .then(function (response) {
        const data = response.data;
        setSystemPrompt(data.prompt);
        setVoice(data.voice);
        setAssistantName(data.assistant_name);
        setAssistantId(data.assistant_id);
        const assistant_id = data.assistant_id;
        console.log(response);
        for (let i = 0; i < uploadedFiles.length; i++) {
          const form = new FormData();
          const file = uploadedFiles[i];
          const bytes = file.bytes;
          form.append("uploaded_file", bytes);
          form.append("file_name", file.name);
          axios.post(`http://${base_url}/knowledge?jwt_token=${access_token}`, form)
            .then((response) => {
              const form = new FormData();
              form.append("assistant_id", assistant_id);
              form.append("knowledge_id", response.data.id);
              axios.post(`http://${base_url}/assistant-knowledge?jwt_token=${access_token}`, form);
            });
        }
      });

    

    setAssistants([...assistants, newAssistant]);
  };

  return (
    <Container maxW="container.xl" py={6} style={{position: 'absolute', width: "80%"}}>
      <Heading mb={6} fontSize={{ base: "2xl", md: "3xl" }} textAlign="left">Assistants Management</Heading>
      <VStack spacing={4} align="stretch">
          <VStack spacing={4} align="center" width="70%" as="form" onSubmit={handleSubmit} bg="white" p={6} borderRadius="md" boxShadow="sm">
            <FormControl isRequired>
              <Flex align="center" mb={2}>
                <FormLabel mb={0} fontSize="md">Assistant Name</FormLabel>
                <Tooltip label="Enter the assistant name" placement="top-start">
                  <InfoIcon ml={2} fontSize="sm" />
                </Tooltip>
              </Flex>
              <Input
                value={assistantName}
                onChange={(e) => setAssistantName(e.target.value)}
                placeholder="Enter assistant name here e.g. John Doe..."
                minHeight="64px"
                resize="vertical"
                fontSize="sm"
              />
            </FormControl>
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
                <option value="ash">Ash</option>
                <option value="ballad">Ballad</option>
                <option value="coral">Coral</option>
                <option value="sage">Sage</option>
                <option value="verse">Verse</option>
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

            <StyledDropzone onDrop={(e) => handleFileUpload(e)} />

            <Button type="submit" colorScheme="blue" size="md">Create Assistant</Button>
          </VStack>

          <Box bg="gray.50" p={6} borderRadius="md" boxShadow="sm" height="100%" width="70%">
            <Heading size="md" mb={4} textAlign="left">Existing Assistants</Heading>
            {assistants.length > 0 ? (
              <VStack spacing={4} align="stretch">
                {assistants.map((assistant, index) => (
                  <Box key={index} borderWidth={1} borderRadius="md" p={4} bg="white">
                    <Text fontSize="sm"><strong>Name:</strong> {assistant.assistantName}</Text>
                    <Text fontSize="sm"><strong>System Prompt:</strong> {assistant.systemPrompt.substring(0, 50)}...</Text>
                    <Text fontSize="sm" mt={2}><strong>Voice:</strong> {assistant.voice}</Text>
                    <HStack spacing={2} mt={3}>
                      <Button leftIcon={<EditIcon />} colorScheme="blue" size="sm">Edit</Button>
                      <Button leftIcon={<DeleteIcon />} colorScheme="red" size="sm" onClick={() => {setAssistants(assistants.filter((item) => {console.log(item, assistant); return item.assistant_id !== assistant.assistant_id}));}}>Delete</Button>
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
