import React, { useState } from 'react';
import { ChakraProvider, Box, Flex, Text, VStack, HStack, IconButton, useMediaQuery } from '@chakra-ui/react';
import { BrowserRouter as Router, Route, Routes, NavLink, useLocation } from 'react-router-dom';
import { FaHome, FaUser, FaPhone, FaCreditCard, FaCog, FaBars } from 'react-icons/fa';
import Assistants from './components/Assistants';
import Campaigns from './components/Campaigns';
import CallLogs from './components/CallLogs';
import Billing from './components/Billing';
import Settings from './components/Settings';

function App() {
  const [assistants, setAssistants] = useState([]);
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile] = useMediaQuery("(max-width: 768px)");

  const addAssistant = (assistant) => {
    setAssistants([...assistants, assistant]);
  };

  const toggleSidebar = () => {
    setSidebarOpen(!isSidebarOpen);
  };

  const TabContent = () => {
    const location = useLocation();

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
            <VStack as="nav" spacing={0} align="stretch">
              {[
                { icon: FaHome, label: 'Assistants', path: '/assistants' },
                { icon: FaUser, label: 'Campaigns', path: '/campaigns' },
                { icon: FaPhone, label: 'Call Logs', path: '/call-logs' },
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
        <Box flex={1} overflowY="auto" bg="white" p={4}>
          <Routes>
            <Route path="/" element={<Assistants assistants={assistants} addAssistant={addAssistant} />} />
            <Route path="/assistants" element={<Assistants assistants={assistants} addAssistant={addAssistant} />} />
            <Route path="/campaigns" element={<Campaigns assistants={assistants} />} />
            <Route path="/call-logs" element={<CallLogs />} />
            <Route path="/billing" element={<Billing />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Assistants assistants={assistants} addAssistant={addAssistant} />} />
          </Routes>
        </Box>
      </Flex>
    );
  };

  return (
    <ChakraProvider>
      <Router>
        <Flex h="100vh" flexDirection={isMobile ? "column" : "row"}>
          <TabContent />
        </Flex>
      </Router>
    </ChakraProvider>
  );
}

export default App;