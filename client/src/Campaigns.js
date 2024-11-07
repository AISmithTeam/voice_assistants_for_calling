import React, { useState, useEffect } from 'react';
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
  Container,
} from '@chakra-ui/react';
import { EditIcon, DeleteIcon, InfoIcon } from '@chakra-ui/icons';
import { FaPlay } from "react-icons/fa"
import axios from 'axios';

const Campaigns = ({ assistants, phoneNumbers }) => {
  const base_url = '127.0.0.1:5000';
  const access_token = localStorage.getItem("access_token");
  const [daysOfWeek, setDaysOfWeek] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [assistantId, setAssistantId] = useState(0);
  const [assistant, setAssistant] = useState(''); // fixme должно быть имя ассистента, пока промпт
  const [maxCallsToClient, setMaxCallsToClient] = useState(0);
  const [recallInterval, setRecallInterval] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [campaignDaysOfWeek, setCampaignDaysOfWeek] = useState([]);
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('18:00');
  const [campaignType, setCampaignType] = useState('');
  const [numberId, setNumberId] = useState(0);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [campaignStatus, setCampaignStatus] = useState('');
  const [campaignId, setCampaignId] = useState(0);
  const [isMobile] = useMediaQuery("(max-width: 768px)");

  // TODO извлечение существующих кампаний при загрузке страницы

  const handleRunCampaign = (campaign_id) => {
    axios
      .post(`http://${base_url}/run-campaign?jwt_token=${access_token}&campaign_id=${campaign_id}`);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newCampaign = {
      assistant,
      maxCallsToClient,
      uploadedFile,
      campaignDaysOfWeek,
      startTime,
      endTime,
      campaignType,
      campaignStatus,
      phoneNumber
    };

    const form = new FormData();
    form.append("assistant_id", assistantId);
    form.append("phone_number_id", numberId);
    form.append("campaign_type", campaignType);
    form.append("start_time", startTime);
    form.append("end_time", endTime);
    form.append("max_recalls", maxCallsToClient);
    form.append("recall_interval", recallInterval);
    form.append("uploaded_file", uploadedFile);
    form.append("file_name", uploadedFileName);
    form.append("campaign_status", "stopped");

    await axios
      .post(`http://${base_url}/campaigns?jwt_token=${access_token}`, form)
      .then(function (response) {
        const data = response.data;
        setPhoneNumber(phoneNumbers.find( (phoneNumber) => phoneNumber.phoneNumberId === data.phone_number_id ).phoneNumber);
        setAssistant(assistants.find( (assistant) => assistant.assistant_id === data.assistant_id ).systemPrompt);
        setRecallInterval(data.recall_interval);
        setCampaignStatus(data.campaign_status);
        setMaxCallsToClient(data.max_recalls);
        setCampaignType(data.campaign_type);
        setStartTime(data.start_time);
        setCampaignId(data.id);
        setEndTime(data.end_time);
        
        for (let i=0; i < campaignDaysOfWeek.length; i++) {
          axios.post(`http://${base_url}/campaign-days-of-week?jwt_token=${access_token}&campaign_id=${data.id}&day_of_week_id=${campaignDaysOfWeek[i].dayOfWeekId}`);
        }
      });

    

    setCampaigns([...campaigns, newCampaign]);
    //setAssistant('');
    //setMaxCallsToClient(0);
    //setUploadedFile(null);
    //setUploadStatus('');
    //setUploadProgress(0);
    //setDaysOfWeek([]);
    //setStartTime('09:00');
    //setEndTime('18:00');
    //setCampaignType('');
    //setNumbers('');
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file && (file.type === 'text/csv' || file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
      setUploadedFile(file);
      setUploadedFileName(file.name);
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


  useEffect(() => {
    axios
      .get(`http://${base_url}/days-of-week?jwt_token=${access_token}&campaign_id=${campaignId}`)
        .then(function (response) {
          const data = response.data;
          var daysOfWeekList = [];
          var dayOfWeekId, dayOfWeek;
          for (var i=0; i < data.length; i++) {
            dayOfWeekId = data[i].id;
            dayOfWeek = data[i].day_of_week;
            daysOfWeekList.push({ dayOfWeekId, dayOfWeek});
          }
          setDaysOfWeek(daysOfWeekList);
        });
  }, [access_token, campaignId]);

  useEffect(() => {
    axios
      .get(`http://${base_url}/campaigns?jwt_token=${access_token}`)
      .then(function (response) {
        const data = response.data;
        var userCampaigns = [];
        var campaignId, assistant, dayOfWeekId, dayOfWeek, maxCallsToClient, startTime, endTime, campaignType, phoneNumber, campaignStatus, uploadedFile;
        for (let i=0; i < data.length; i++) {
          var campaignDaysOfWeek = [];
          campaignId = data[i].id;
          phoneNumber = phoneNumbers.find( (phoneNumber) => phoneNumber.phoneNumberId === data[i].phone_number_id ).phoneNumber;
          assistant = assistants.find( (assistant) => assistant.assistant_id === data[i].assistant_id ).assistantName;
          maxCallsToClient = data[i].max_recalls;
          startTime = data[i].start_time;
          endTime = data[i].end_time;
          campaignType = data[i].type;
          campaignStatus = data[i].status;
          uploadedFile = data[i].uploaded_file;
          for (let j=0; j < data[i].days_of_week.length; j++) {
            dayOfWeekId = data[i].days_of_week[j].day_of_week_id;
            console.log(daysOfWeek.find( (dayOfWeek) => dayOfWeek.dayOfWeekId === dayOfWeekId ));
            if (typeof daysOfWeek.find( (dayOfWeek) => dayOfWeek.dayOfWeekId === dayOfWeekId ) !== 'undefined') {
              dayOfWeek = daysOfWeek.find( (dayOfWeek) => dayOfWeek.dayOfWeekId === dayOfWeekId ).dayOfWeek;
              campaignDaysOfWeek.push({ dayOfWeekId, dayOfWeek});
            }
          }

          // fixme add upload file
          userCampaigns.push({ 
            campaignId,
            assistant,
            maxCallsToClient,
            campaignDaysOfWeek,
            startTime,
            endTime,
            campaignType,
            phoneNumber,
            campaignStatus,
            uploadedFile
          });
        }
        setCampaigns(userCampaigns);
      });
      console.log("AFTER REQUEST");
  }, [access_token, assistants, daysOfWeek, phoneNumbers]);

  const handleDayChange = (day) => {
    setCampaignDaysOfWeek(prev =>
      prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]
    );
  };
  //<Grid templateColumns={{ base: "1fr", md: "1fr 1fr" }} gap={6} maxWidth="100%" px={[2, 4, 6]}>
  /////////////////////////////////////////////////////////////
  return (
  <Container maxW="container.xl" py={6} style={{position: 'absolute', width: "80%"}}>  
    <VStack width={"70%"} align={"center"}>
      <Box width={"100%"}>
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
              <Select size="sm" value={assistantId} onChange={(e) => setAssistantId(e.target.value)}>
                <option value="">Select an assistant</option>
                {assistants.map((assistant, index) => (
                  <option key={index} value={assistant.assistant_id}>
                    {assistant.assistantName}
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
            <FormControl isRequired>
              <FormLabel mb={1}>
                Recalls Interval
                <Tooltip label="Set the recall interval in seconds" placement="top-start">
                  <InfoIcon ml={2} />
                </Tooltip>
              </FormLabel>
              <NumberInput size="sm" value={recallInterval} onChange={(value) => setRecallInterval(Number(value))}>
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>
          </SimpleGrid>
          <FormControl>
            <FormLabel mb={1}>
              Days of Week
              <Tooltip label="Select the days on which the campaign will run" placement="top-start">
                <InfoIcon ml={2} />
              </Tooltip>
            </FormLabel>
            <HStack flexWrap="wrap" spacing={2}>
              {daysOfWeek.map((day, index) => (
                <Checkbox
                  key={day}
                  size="sm"
                  isChecked={campaignDaysOfWeek.includes(day)}
                  onChange={() => handleDayChange(day)}
                >
                  {day.dayOfWeek}
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
              <Select size="sm" value={numberId} onChange={(e) => setNumberId(e.target.value)}>
                <option value="">Select a Number</option>
                {phoneNumbers.map((phoneNumber, index) => (
                  <option key={index} value={phoneNumber.phoneNumberId}>
                    {phoneNumber.phoneNumber}
                  </option>
                ))}
              </Select>
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
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={3}>
            {campaigns.map((campaign, index) => (
              <Card key={index} size="sm">
                <CardHeader py={2}>
                  <Heading size="sm">Campaign {campaign.campaignId}</Heading>
                </CardHeader>
                <CardBody py={2}>
                  <Text fontSize="xs"><strong>Assistant:</strong> {campaign.assistant.substring(0, 30)}...</Text>
                  <Text fontSize="xs"><strong>Max Calls:</strong> {campaign.maxCallsToClient}</Text>
                  <Text fontSize="xs"><strong>Days:</strong> {campaign.campaignDaysOfWeek.map((dayOfWeek) => dayOfWeek.dayOfWeek).join(', ')}</Text>
                  <Text fontSize="xs"><strong>Time:</strong> {`${campaign.startTime} - ${campaign.endTime}`}</Text>
                  <Text fontSize="xs"><strong>Type:</strong> {campaign.campaignType}</Text>
                  <Text fontSize="xs"><strong>Number:</strong> {campaign.phoneNumber.substring(0, 20)}</Text>
                  <Text fontSize="xs"><strong>Status:</strong> {campaign.campaignStatus}</Text>
                  <Text fontSize="xs"><strong>File:</strong> {campaign.uploadedFile ? campaign.uploadedFile.name : 'No file'}</Text>
                </CardBody>
                <CardFooter py={2}>
                  <HStack spacing={2}>
                    <IconButton icon={<EditIcon />} aria-label="Edit" size="sm" />
                    <IconButton icon={<DeleteIcon />} aria-label="Delete" size="sm" onClick={() => {setCampaigns(campaigns.filter((item) => {return item.campaignId !== campaign.campaignId}));}}/>
                    <IconButton icon={<FaPlay />} size="sm" title='click to run calling campaign' onClick={() => handleRunCampaign(campaign.campaignId)}/>
                  </HStack>
                </CardFooter>
              </Card>
            ))}
          </SimpleGrid>
        </Box>
      )}
    </VStack>
  </Container>
  );
};

export default Campaigns;
