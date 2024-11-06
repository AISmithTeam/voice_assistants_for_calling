import React, { useState, useEffect, useRef } from 'react';
import axios from "axios";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Heading,
  Select,
  Textarea,
  Input,
  VStack,
  HStack,
  Stack,
  Text,
  Grid,
  GridItem,
  Flex,
  Tooltip,
  Container,
  useMediaQuery,
} from '@chakra-ui/react';
import { InfoIcon, EditIcon, DeleteIcon } from '@chakra-ui/icons';


const PhoneNumbers = ({userPhoneNumbers}) => {
  const base_url = '127.0.0.1:5000';
  const [isMobile] = useMediaQuery("(max-width: 768px)");
  const access_token = localStorage.getItem("access_token");

  const [phoneNumber, setPhoneNumber] = useState('');
  const [accountSid, setAccountSid] = useState('');
  const [authToken, setAuthToken] = useState('');
  const [phoneNumberId, setPhoneNumberId] = useState(0);
  const [phoneNumbers, setPhoneNumbers] = useState([]);
  
  useEffect(() => setPhoneNumbers(userPhoneNumbers), []);

  const submitRef = useRef();

  /*useEffect(() => {
    const url = `http://${base_url}/phone-numbers?jwt_token=${access_token}`;
    axios
      .get(url)
      .then(function (response) {
        const data = response.data;
        var userPhoneNumbers = [];
        var phoneNumberId, phoneNumber, accountSid, authToken;
        for (var i=0; i < data.length; i++) {
          phoneNumberId = data[i].phone_number_id;
          phoneNumber = data[i].phone_number;
          accountSid = data[i].account_sid;
          authToken = data[i].auth_token;
          userPhoneNumbers.push( { accountSid, authToken, phoneNumber, phoneNumberId } );
        }
        setPhoneNumbers(userPhoneNumbers);
      });
  }, []);*/


  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("submit");

    const newPhoneNumber = { accountSid, authToken, phoneNumber, phoneNumberId };
    setPhoneNumbers([...phoneNumbers, newPhoneNumber]);
    //setAccountSid('');
    //setAuthToken('');

    axios
      .post(`http://${base_url}/phone-numbers?jwt_token=${access_token}`, {
        phone_number: phoneNumber,
        account_sid: accountSid,
        auth_token: authToken
      })
      .then(function (response) {
        setPhoneNumber(response.phone_number);
        setAccountSid(response.account_sid);
        setAuthToken(response.auth_token);
        setPhoneNumberId(response.phone_number_id);
      });
  };

  return (
    <Container maxW="container.xl" py={6} style={{position: 'absolute', width: "80%"}}>
      <Heading mb={6} fontSize={{ base: "2xl", md: "3xl" }} textAlign="left">Phone Numbers Management</Heading>
        <VStack spacing={4} align="stretch" onSubmit={handleSubmit}>
            <Stack direction={isMobile ? "column" : "row"} spacing={4} align="center" width="100%" as="form" bg="white" p={6} borderRadius="md" boxShadow="sm">
              <FormControl isRequired>
                <Flex align="center" mb={2}>
                  <FormLabel mb={0} fontSize="md">Phone Number</FormLabel>
                  <Tooltip label="Enter the phone number that will be used in call campaigns" placement="top-start">
                    <InfoIcon ml={2} fontSize="sm" />
                  </Tooltip>
                </Flex>
                <Input
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="Enter phone number..."
                  height="48px"
                  fontSize="sm"
                />
              </FormControl>
              <FormControl>
                <Flex align="center" mb={2}>
                  <FormLabel mb={0} fontSize="md">Account SID</FormLabel>
                  <Tooltip label="Enter the account SID to use phone number" placement="top-start">
                    <InfoIcon ml={2} fontSize="sm" />
                  </Tooltip>
                </Flex>
                <Input
                  value={accountSid}
                  onChange={(e) => setAccountSid(e.target.value)}
                  placeholder="Enter your account SID..."
                  height="48px"
                  fontSize="sm"
                />
              </FormControl>
              <FormControl>
                <Flex align="center" mb={2}>
                  <FormLabel mb={0} fontSize="md">Auth Token</FormLabel>
                  <Tooltip label="Enter the auth token to use phone number" placement="top-start">
                    <InfoIcon ml={2} fontSize="sm" />
                  </Tooltip>
                </Flex>
                <Input
                  value={authToken}
                  onChange={(e) => setAuthToken(e.target.value)}
                  placeholder="Enter auth token..."
                  height="48px"
                  fontSize="sm"
                />
              </FormControl>
              <Button type="submit" ref={submitRef} style={{ display: 'none' }} />
            </Stack>
            <Button 
              onClick={() => submitRef.current.click()}
              colorScheme="blue"
              width={isMobile? "100%" : "32%"}
              left={isMobile ? "0%" : "34%"}>Add Phone Number</Button>
            <Box bg="gray.50" p={6} borderRadius="md" boxShadow="sm" height="100%" width="100%">
              <Heading size="md" mb={4} textAlign="left">Added Phone Numbers</Heading>
              {phoneNumbers.length > 0 ? (
                <VStack spacing={4} align="stretch">
                  {phoneNumbers.map((phoneNumber, index) => (
                    <Box key={index} borderWidth={1} borderRadius="md" p={4} bg="white">
                      <Text fontSize="sm"><strong>Phone Number:</strong> {phoneNumber.phoneNumber}</Text>
                      <Text fontSize="sm" mt={2}><strong>Account SID:</strong> {phoneNumber.accountSid}</Text>
                      <Text fontSize="sm" mt={2}><strong>Auth Token:</strong> {phoneNumber.authToken}</Text>
                      <HStack spacing={2} mt={3}>
                        <Button leftIcon={<EditIcon />} colorScheme="blue" size="sm">Edit</Button>
                        <Button leftIcon={<DeleteIcon />} colorScheme="red" size="sm">Delete</Button>
                      </HStack>
                    </Box>
                  ))}
                </VStack>
              ) : (
                <Text fontSize="sm">No phone numbers added yet.</Text>
              )}
            </Box>
        </VStack>
    </Container>
  );
};

export default PhoneNumbers;
