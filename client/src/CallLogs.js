import React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  FormControl,
  FormLabel,
  Select,
  Button,
  IconButton,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Input,
  Alert,
  AlertIcon,
  Progress,
  Text,
  Checkbox,
  HStack,
  Textarea,
  Tooltip,
  useMediaQuery,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Grid,
} from '@chakra-ui/react';
import { EditIcon, DeleteIcon, InfoIcon } from '@chakra-ui/icons';

const Campaigns = ({ assistants = [] }) => {
  const [campaigns, setCampaigns] = useState([]);
  const [assistant, setAssistant] = useState('');
  const [maxCallsToClient, setMaxCallsToClient] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [daysOfWeek, setDaysOfWeek] = useState([]);
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('18:00');
  const [campaignType, setCampaignType] = useState('');
  const [numbers, setNumbers] = useState('');
  const [isMobile] = useMediaQuery("(max-width: 768px)");

  const handleSubmit = (e) => {
    e.preventDefault();
    const newCampaign = {
      assistant,
      maxCallsToClient,
      uploadedFile,
      daysOfWeek,
      startTime,
      endTime,
      campaignType,
      numbers
    };
    setCampaigns([...campaigns, newCampaign]);
    setAssistant('');
    setMaxCallsToClient(0);
    setUploadedFile(null);
    setUploadStatus('');
    setUploadProgress(0);
    setDaysOfWeek([]);
    setStartTime('09:00');
    setEndTime('18:00');
    setCampaignType('');
    setNumbers('');
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file && (file.type === 'text/csv' || file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
      setUploadedFile(file);
      setUploadStatus('uploading');
      // Simulating upload progress
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
  };

  const handleDayChange = (day) => {
    setDaysOfWeek(prev =>
      prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]
    );
  };

  return (
    <Grid templateColumns={{ base: "1fr", md: "1fr 1fr" }} gap={6} maxWidth="100%" px={[2, 4, 6]}>
      <Box>
        <Heading mb={3} fontSize={{ base: "xl", md: "2xl" }}>Campaigns Management</Heading>
        <VStack spacing={3} as="form" onSubmit={handleSubmit} align="stretch">
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
            <FormControl isRequired>
              <FormLabel mb={1}>
                Assistant
                <Tooltip label="Selected assistant will handle calls" placement="top-start">
                  <InfoIcon ml={2} />
                </Tooltip>
              </FormLabel>
              <Select size="sm" value={assistant} onChange={(e) => setAssistant(e.target.value)}>
                <option value="">Select an assistant</option>
                {assistants.map((assistant, index) => (
                  <option key={index} value={assistant.systemPrompt}>
                    {assistant.systemPrompt.substring(0, 30)}...
                  </option>
                ))}
              </Select>
            </FormControl>
            <FormControl isRequired>
              <FormLabel mb={1}>
                Maximum Calls to Client
                <Tooltip label="Set the maximum number of calls allowed to a single client" placement="top-start">
                  <InfoIcon ml={2} />
                </Tooltip>
              </FormLabel>
              <NumberInput size="sm" value={maxCallsToClient} onChange={(value) => setMaxCallsToClient(Number(value))}>
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>
          </SimpleGrid>
          <FormControl isRequired>
            <FormLabel mb={1}>
              Days of Week
              <Tooltip label="Select the days on which the campaign will run" placement="top-start">
                <InfoIcon ml={2} />
              </Tooltip>
            </FormLabel>
            <HStack flexWrap="wrap" spacing={2}>
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
                <Checkbox
                  key={day}
                  size="sm"
                  isChecked={daysOfWeek.includes(day)}
                  onChange={() => handleDayChange(day)}
                >
                  {day}
                </Checkbox>
              ))}
            </HStack>
          </FormControl>
          <FormControl isRequired>
            <FormLabel mb={1}>
              Campaign Time Interval
              <Tooltip label="Set the daily time range for the campaign" placement="top-start">
                <InfoIcon ml={2} />
              </Tooltip>
            </FormLabel>
            <HStack>
              <Input
                size="sm"
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
              />
              <Text>to</Text>
              <Input
                size="sm"
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
              />
            </HStack>
          </FormControl>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
            <FormControl isRequired>
              <FormLabel mb={1}>
                Campaign Type
                <Tooltip label="Choose between outbound or inbound campaign" placement="top-start">
                  <InfoIcon ml={2} />
                </Tooltip>
              </FormLabel>
              <Select size="sm" value={campaignType} onChange={(e) => setCampaignType(e.target.value)}>
                <option value="">Select campaign type</option>
                <option value="outbound">Outbound</option>
                <option value="inbound">Inbound</option>
              </Select>
            </FormControl>
            <FormControl isRequired>
              <FormLabel mb={1}>
                Numbers to Use in Campaign
                <Tooltip label="Enter the phone numbers to be used in this campaign" placement="top-start">
                  <InfoIcon ml={2} />
                </Tooltip>
              </FormLabel>
              <Textarea
                size="sm"
                value={numbers}
                onChange={(e) => setNumbers(e.target.value)}
                placeholder="Enter numbers, separated by commas"
              />
            </FormControl>
          </SimpleGrid>
          <FormControl>
            <FormLabel mb={1}>
              Upload CSV or Excel File
              <Tooltip label="Upload a file containing additional campaign data" placement="top-start">
                <InfoIcon ml={2} />
              </Tooltip>
            </FormLabel>
            <Input size="sm" type="file" accept=".csv,.xlsx" onChange={handleFileUpload} />
            {uploadedFile && (
              <Text mt={1} fontSize="xs">
                Selected file: {uploadedFile.name}
              </Text>
            )}
            {uploadStatus === 'uploading' && (
              <Progress value={uploadProgress} mt={1} size="xs" colorScheme="blue" />
            )}
            {uploadStatus === 'success' && (
              <Alert status="success" mt={1} size="sm">
                <AlertIcon />
                File uploaded successfully!
              </Alert>
            )}
            {uploadStatus === 'error' && (
              <Alert status="error" mt={1} size="sm">
                <AlertIcon />
                Please upload a CSV or Excel file
              </Alert>
            )}
          </FormControl>
          <Button type="submit" colorScheme="blue" size="md">Create Campaign</Button>
        </VStack>
      </Box>

      {campaigns.length > 0 && (
        <Box>
          <Heading size="md" mb={3}>Existing Campaigns</Heading>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
            {campaigns.map((campaign, index) => (
              <Card key={index} size="sm">
                <CardHeader py={2}>
                  <Heading size="sm">Campaign {index + 1}</Heading>
                </CardHeader>
                <CardBody py={2}>
                  <Text fontSize="xs"><strong>Assistant:</strong> {campaign.assistant.substring(0, 30)}...</Text>
                  <Text fontSize="xs"><strong>Max Calls:</strong> {campaign.maxCallsToClient}</Text>
                  <Text fontSize="xs"><strong>Days:</strong> {campaign.daysOfWeek.join(', ')}</Text>
                  <Text fontSize="xs"><strong>Time:</strong> {`${campaign.startTime} - ${campaign.endTime}`}</Text>
                  <Text fontSize="xs"><strong>Type:</strong> {campaign.campaignType}</Text>
                  <Text fontSize="xs"><strong>Numbers:</strong> {campaign.numbers.substring(0, 20)}...</Text>
                  <Text fontSize="xs"><strong>File:</strong> {campaign.uploadedFile ? campaign.uploadedFile.name : 'No file'}</Text>
                </CardBody>
                <CardFooter py={2}>
                  <HStack spacing={2}>
                    <IconButton icon={<EditIcon />} aria-label="Edit" size="xs" />
                    <IconButton icon={<DeleteIcon />} aria-label="Delete" size="xs" />
                  </HStack>
                </CardFooter>
              </Card>
            ))}
          </SimpleGrid>
        </Box>
      )}
    </Grid>
  );
};

export default Campaigns;
