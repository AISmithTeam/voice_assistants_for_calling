import React, { useEffect, useState } from 'react';
import { ChakraProvider, Box, Flex, Text, VStack, HStack, IconButton, useMediaQuery } from '@chakra-ui/react';
import { Route, Routes, NavLink, Navigate } from 'react-router-dom';
import { FaHome, FaUser, FaPhone, FaCreditCard, FaCog, FaBars, FaClipboardList } from 'react-icons/fa';
import Login from './Login';
import Assistants from './Assistants';
import Campaigns from './Campaigns';
import CallLogs from './CallLogs';
import Billing from './Billing';
import Settings from './Settings';
import PhoneNumbers from './phoneNumbers';
import axios from 'axios'; 

function App() {
  const base_url = '127.0.0.1:5000';
  const access_token = localStorage.getItem("access_token");

  const [assistants, setAssistants] = useState([]);
  const [phoneNumbers, setPhoneNumbers] = useState([]);
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile] = useMediaQuery("(max-width: 768px)");  
  
  useEffect(() => {
    const fetch_assistants = async () => {
      const url = `http://${base_url}/assistants?jwt_token=${access_token}`;
      axios
        .get(url)
        .then(function (response) {
          const data = response.data;
          var user_assistants = [];
          var assistant_id, systemPrompt, voice;
          for (var i=0; i < data.length; i++) {
            assistant_id = data[i].id;
            systemPrompt = data[i].prompt;
            voice = data[i].voice;
            user_assistants.push( { systemPrompt, voice, assistant_id } );
          }
          setAssistants(user_assistants);
        });
      };
    fetch_assistants();
  }, [access_token]);

  useEffect(() => {
    const fetch_numbers = async () => {
      const url = `http://${base_url}/phone-numbers?jwt_token=${access_token}`;
      axios
        .get(url)
        .then(function (response) {
          const data = response.data;
          var userPhoneNumbers = [];
          var phoneNumberId, phoneNumber, accountSid, authToken;
          for (var i=0; i < data.length; i++) {
            phoneNumberId = data[i].id;
            phoneNumber = data[i].phone_number;
            accountSid = data[i].account_sid;
            authToken = data[i].auth_token;
            userPhoneNumbers.push( { accountSid, authToken, phoneNumber, phoneNumberId } );
          }
          setPhoneNumbers(userPhoneNumbers);
        });
    };
    fetch_numbers();
  }, [access_token]);

  const addAssistant = (assistant) => {
    setAssistants([...assistants, assistant]);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  const TabContent = () => {
    //const location = useLocation();
    //const [authenticated, setauthenticated] = useState(localStorage.getItem(localStorage.getItem("authenticated")));
    //const [access_token, setaccesstoken] = useState(localStorage.getItem(localStorage.getItem("access_token")));
    
    const loggedInUser = localStorage.getItem("authenticated");
    //if (loggedInUser) {
      //setauthenticated(loggedInUser);
      //setaccesstoken(localStorage.getItem("access_token"));
    //}

    if (!loggedInUser) {
      return <Navigate replace to="/login" />;
    }

    return (
      <Flex>
        {isMobile && (
          <IconButton
            icon={<FaBars />}
            onClick={toggleSidebar}
            position="absolute"
            top={2}
            left={2}
            zIndex={2}
          />
        )}
        <Box
          bg="#1E2329"
          w={isMobile ? (isSidebarOpen ? "100%" : "0") : (isSidebarOpen ? "250px" : "60px")}
          color="white"
          transition="width 0.3s"
          overflow="hidden"
          position={isMobile ? "absolute" : "relative"}
          h={isMobile ? "auto" : "100%"}
          zIndex={1}
        >
          <VStack align="stretch" spacing={0} h="100%">
            <Box p={4} display={isSidebarOpen ? "block" : "none"}>
              <Text fontSize="xl" fontWeight="bold" color="#64B5F6">DASHBOARD</Text>
            </Box>
            <VStack as="nav" spacing={0} align="stretch" height="100%">
              {[
                { icon: FaHome, label: 'Assistants', path: '/assistants' },
                { icon: FaUser, label: 'Campaigns', path: '/campaigns' },
                { icon: FaPhone, label: 'Phone Numbers', path: '/phone-numbers'},
                { icon: FaClipboardList, label: 'Call Logs', path: '/call-logs' },
                { icon: FaCreditCard, label: 'Billing', path: '/billing' },
                { icon: FaCog, label: 'Settings', path: '/settings' },
              ].map(({ icon: Icon, label, path }) => (
                  <NavLink
                    key={label}
                    to={path}
                    style={({ isActive }) => ({
                      backgroundColor: isActive ? "#171B20" : "transparent",
                      borderLeft: isActive && isSidebarOpen ? "4px solid #64B5F6" : "none",
                      textDecoration: "none",
                      color: "white",
                    })}
                  >
                    <HStack
                      py={4}
                      px={4}
                      spacing={3}
                      _hover={{ bg: "#2C3540" }}
                    >
                      <Icon />
                      {isSidebarOpen && <Text>{label}</Text>}
                    </HStack>
                  </NavLink>
              ))}
            </VStack>
          </VStack>
        </Box>
        <Box flex={1} overflowY="auto" bg="white" p={4} height="100%">
            <Routes>
                <Route path="login" element={<Login />} />
                <Route path="/" element={<Assistants />} />
                <Route path="/assistants" element={<Assistants />} />
                <Route path="/campaigns" element={<Campaigns assistants={assistants} phoneNumbers={phoneNumbers} />} />
                <Route path="/phone-numbers" element={<PhoneNumbers userPhoneNumbers={phoneNumbers} />} />
                <Route path="/call-logs" element={<CallLogs />} />
                <Route path="/billing" element={<Billing />} />
                <Route path="/settings" element={<Settings />} />
            </Routes>
        </Box>
      </Flex>
    );
  };

  return (
    <ChakraProvider>
        <Flex h="300vh" align="stretch" flexDirection={isMobile ? "column" : "row"}>
          <TabContent />
        </Flex>
    </ChakraProvider>
  );
}

export default App;