import React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Stat,
  StatLabel,
  StatNumber,
  StatGroup,
  Input,
  FormControl,
  FormLabel,
  HStack,
  useMediaQuery,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Text,
  Tooltip,
  Flex,
} from '@chakra-ui/react';
import { InfoIcon } from '@chakra-ui/icons';

const Billing = () => {
  const [billingData] = useState([
    { id: 1, date: '2023-05-01', campaign: 'Campaign A', calls: 100, duration: '5:30:00', cost: 150.00 },
    { id: 2, date: '2023-05-02', campaign: 'Campaign B', calls: 75, duration: '3:45:00', cost: 112.50 },
    { id: 3, date: '2023-05-03', campaign: 'Campaign A', calls: 120, duration: '7:15:00', cost: 180.00 },
  ]);

  const [filter, setFilter] = useState({ startDate: '', endDate: '', campaign: '' });
  const [isMobile] = useMediaQuery("(max-width: 768px)");

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilter({ ...filter, [name]: value });
  };

  const filteredBillingData = billingData.filter(item =>
    (filter.startDate === '' || item.date >= filter.startDate) &&
    (filter.endDate === '' || item.date <= filter.endDate) &&
    item.campaign.toLowerCase().includes(filter.campaign.toLowerCase())
  );

  const totalCalls = filteredBillingData.reduce((sum, item) => sum + item.calls, 0);
  const totalDuration = filteredBillingData.reduce((sum, item) => {
    const [hours, minutes, seconds] = item.duration.split(':').map(Number);
    return sum + hours * 3600 + minutes * 60 + seconds;
  }, 0);
  const totalCost = filteredBillingData.reduce((sum, item) => sum + item.cost, 0);

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <Box>
      <Heading mb={4}>Billing</Heading>
      <VStack spacing={4} align="stretch">
        <StatGroup>
          <Stat>
            <Flex align="center">
              <StatLabel>Total Calls</StatLabel>
              <Tooltip label="Total number of calls made" placement="top">
                <InfoIcon ml={2} />
              </Tooltip>
            </Flex>
            <StatNumber>{totalCalls}</StatNumber>
          </Stat>
          <Stat>
            <Flex align="center">
              <StatLabel>Total Duration</StatLabel>
              <Tooltip label="Total duration of all calls" placement="top">
                <InfoIcon ml={2} />
              </Tooltip>
            </Flex>
            <StatNumber>{formatDuration(totalDuration)}</StatNumber>
          </Stat>
          <Stat>
            <Flex align="center">
              <StatLabel>Total Cost</StatLabel>
              <Tooltip label="Total cost of all calls" placement="top">
                <InfoIcon ml={2} />
              </Tooltip>
            </Flex>
            <StatNumber>${totalCost.toFixed(2)}</StatNumber>
          </Stat>
        </StatGroup>
        <SimpleGrid columns={isMobile ? 1 : 3} spacing={4} width="100%">
          <FormControl>
            <Flex align="center">
              <FormLabel mb={0}>Start Date</FormLabel>
              <Tooltip label="Filter by start date" placement="top">
                <InfoIcon ml={2} />
              </Tooltip>
            </Flex>
            <Input
              type="date"
              name="startDate"
              value={filter.startDate}
              onChange={handleFilterChange}
            />
          </FormControl>
          <FormControl>
            <Flex align="center">
              <FormLabel mb={0}>End Date</FormLabel>
              <Tooltip label="Filter by end date" placement="top">
                <InfoIcon ml={2} />
              </Tooltip>
            </Flex>
            <Input
              type="date"
              name="endDate"
              value={filter.endDate}
              onChange={handleFilterChange}
            />
          </FormControl>
          <FormControl>
            <Flex align="center">
              <FormLabel mb={0}>Campaign</FormLabel>
              <Tooltip label="Filter by campaign name" placement="top">
                <InfoIcon ml={2} />
              </Tooltip>
            </Flex>
            <Input
              type="text"
              name="campaign"
              value={filter.campaign}
              onChange={handleFilterChange}
              placeholder="Filter by campaign"
            />
          </FormControl>
        </SimpleGrid>
        {isMobile ? (
          <SimpleGrid columns={1} spacing={4}>
            {filteredBillingData.map((item) => (
              <Card key={item.id}>
                <CardHeader>
                  <Heading size="md">{item.campaign}</Heading>
                </CardHeader>
                <CardBody>
                  <Text><strong>Date:</strong> {item.date}</Text>
                  <Text><strong>Calls:</strong> {item.calls}</Text>
                  <Text><strong>Duration:</strong> {item.duration}</Text>
                  <Text><strong>Cost:</strong> ${item.cost.toFixed(2)}</Text>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        ) : (
          <Box overflowX="auto" width="100%">
            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th>Date</Th>
                  <Th>Campaign</Th>
                  <Th>Calls</Th>
                  <Th>Duration</Th>
                  <Th>Cost</Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredBillingData.map((item) => (
                  <Tr key={item.id}>
                    <Td>{item.date}</Td>
                    <Td>{item.campaign}</Td>
                    <Td>{item.calls}</Td>
                    <Td>{item.duration}</Td>
                    <Td>${item.cost.toFixed(2)}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default Billing;
