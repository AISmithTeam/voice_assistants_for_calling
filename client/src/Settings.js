import React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Select,
  Switch,
  Button,
  useToast,
  SimpleGrid,
  useMediaQuery,
  Tooltip,
  Flex,
} from '@chakra-ui/react';
import { InfoIcon } from '@chakra-ui/icons';

const Settings = () => {
  const [settings, setSettings] = useState({
    username: '',
    email: '',
    language: 'en',
    timezone: 'UTC',
    notifications: true,
    darkMode: false,
  });

  const toast = useToast();
  const [isMobile] = useMediaQuery("(max-width: 768px)");

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSettings({ ...settings, [name]: value });
  };

  const handleSwitchChange = (name) => {
    setSettings({ ...settings, [name]: !settings[name] });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Here you would typically send the settings to a backend API
    console.log('Settings saved:', settings);
    toast({
      title: 'Settings saved.',
      description: 'Your preferences have been updated.',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  return (
    <Box>
      <Heading mb={4}>Settings</Heading>
      <form onSubmit={handleSubmit}>
        <VStack spacing={4} align="stretch" width="100%">
          <SimpleGrid columns={isMobile ? 1 : 2} spacing={4} width="100%">
            <FormControl>
              <Flex align="center">
                <FormLabel mb={0}>Username</FormLabel>
                <Tooltip label="Enter your preferred username" placement="top">
                  <InfoIcon ml={2} />
                </Tooltip>
              </Flex>
              <Input
                name="username"
                value={settings.username}
                onChange={handleInputChange}
              />
            </FormControl>
            <FormControl>
              <Flex align="center">
                <FormLabel mb={0}>Email</FormLabel>
                <Tooltip label="Enter your email address" placement="top">
                  <InfoIcon ml={2} />
                </Tooltip>
              </Flex>
              <Input
                name="email"
                type="email"
                value={settings.email}
                onChange={handleInputChange}
              />
            </FormControl>
          </SimpleGrid>
          <SimpleGrid columns={isMobile ? 1 : 2} spacing={4} width="100%">
            <FormControl>
              <Flex align="center">
                <FormLabel mb={0}>Language</FormLabel>
                <Tooltip label="Select your preferred language" placement="top">
                  <InfoIcon ml={2} />
                </Tooltip>
              </Flex>
              <Select
                name="language"
                value={settings.language}
                onChange={handleInputChange}
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
              </Select>
            </FormControl>
            <FormControl>
              <Flex align="center">
                <FormLabel mb={0}>Timezone</FormLabel>
                <Tooltip label="Select your timezone" placement="top">
                  <InfoIcon ml={2} />
                </Tooltip>
              </Flex>
              <Select
                name="timezone"
                value={settings.timezone}
                onChange={handleInputChange}
              >
                <option value="UTC">UTC</option>
                <option value="EST">Eastern Standard Time</option>
                <option value="PST">Pacific Standard Time</option>
              </Select>
            </FormControl>
          </SimpleGrid>
          <SimpleGrid columns={isMobile ? 1 : 2} spacing={4} width="100%">
            <FormControl display="flex" alignItems="center">
              <Flex align="center" flex="1">
                <FormLabel htmlFor="notifications" mb="0">
                  Enable Notifications
                </FormLabel>
                <Tooltip label="Toggle notifications on/off" placement="top">
                  <InfoIcon ml={2} />
                </Tooltip>
              </Flex>
              <Switch
                id="notifications"
                isChecked={settings.notifications}
                onChange={() => handleSwitchChange('notifications')}
              />
            </FormControl>
            <FormControl display="flex" alignItems="center">
              <Flex align="center" flex="1">
                <FormLabel htmlFor="darkMode" mb="0">
                  Dark Mode
                </FormLabel>
                <Tooltip label="Toggle dark mode on/off" placement="top">
                  <InfoIcon ml={2} />
                </Tooltip>
              </Flex>
              <Switch
                id="darkMode"
                isChecked={settings.darkMode}
                onChange={() => handleSwitchChange('darkMode')}
              />
            </FormControl>
          </SimpleGrid>
          <Button type="submit" colorScheme="blue" size={isMobile ? "md" : "lg"} width="100%">
            Save Settings
          </Button>
        </VStack>
      </form>
    </Box>
  );
};

export default Settings;
