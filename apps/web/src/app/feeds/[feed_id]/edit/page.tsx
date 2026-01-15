"use client";

import {
  Box,
  Heading,
  Input,
  Button,
  Flex,
  Text,
  useDisclosure,
  Accordion,
  HStack
} from '@chakra-ui/react';
import { useParams } from 'next/navigation';

import { useToast } from "@chakra-ui/toast";
import {
  FormControl,
} from "@chakra-ui/form-control";
import { FiPlus, FiTrash, FiRss, FiList } from "react-icons/fi";
import axios from 'axios';
import Cookies from "js-cookie";
import { useEffect, useState } from 'react';
import { Feed, Picker } from '@/types/Feed';
import { AddPickerModal } from '@/app/feeds/[feed_id]/edit/_components/add-picker-modal';


export default function FeedPage() {
  const params = useParams();
  const feedId = params.feed_id as string;
  const [data, setData] = useState<Feed>();
  const [pickers, setPickers] = useState<Picker[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newName, setNewName] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const {
    open: isPickerModalOpen, onOpen: onOpenPickerModal, onClose: onClosePickerModal
  } = useDisclosure();
  const toast = useToast();

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const token = Cookies.get("token");
      const feedRes = await axios.get("/api/v1/feeds/" + feedId, {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });
      setData(feedRes.data);
      setNewName(feedRes.data.name);
      setPickers(feedRes.data.pickers || []);
    } catch (error: unknown) {
      console.error("Error fetching data:", error);
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          Cookies.remove("token");
          window.location.href = "/login";
        } else {
          console.error("Axios error:", error.message);
        }
      } else {
        console.error("Unexpected error:", error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [feedId]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUpdating(true);

    if (!newName.trim()) {
      setIsUpdating(false);
      return;
    }

    try {
      const token = Cookies.get("token");
      await axios.patch(`/api/v1/feeds/${feedId}`, { name: newName }, {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });
      toast(
        {
          title: "Success",
          description: "Feed name updated.",
          status: "success",
          duration: 3000,
          isClosable: true
        });
      fetchData();
    } catch (error: unknown) {
      toast(
        {
          title: "Error",
          description: "Failed to update feed name.",
          status: "error",
          duration: 5000,
          isClosable: true
        }
      );
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          Cookies.remove("token");
          window.location.href = "/login";
        } else {
          console.error("Axios error:", error.message);
        }
      } else {
        console.error("Unexpected error:", error);
      }
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return <Box p={6}><p>Loading feed settings...</p></Box>;
  }

  const handleDelete = async (externalId: string) => {
    if (!window.confirm(`Are you sure you want to delete picker ID: ${externalId}?`)) {
      return;
    }

    try {
      const token = Cookies.get("token");
      await axios.delete(`/api/v1/pickers/${externalId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });

      toast({
        title: "Picker Deleted.",
        description: `${externalId} was successfully removed.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      fetchData();

    } catch (error: unknown) {
      console.error("Error deleting picker:", error);
      toast({
        title: "Error.",
        description: `Failed to delete ${externalId}.`,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          Cookies.remove("token");
          window.location.href = "/login";
        } else {
          console.error("Axios error:", error.message);
        }
      } else {
        console.error("Unexpected error:", error);
      }
    }
  };

  return (
    <Box p={0}>
      <Flex justifyContent="space-between" alignItems="flex-start" p={0}>
        <Box>
          <Heading as="h2" size="lg" mt={0} mb={4}>
            Feed Name
          </Heading>
          <Box as="form" onSubmit={handleUpdate} maxW="175px">
            <FormControl id="feed-name" mb={4}>
              <Input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Enter new feed name and press Enter"
                required
              />
            </FormControl>
            <Box fontSize="xs" color="gray.600" mt="10px">
              {data?.external_id}
            </Box>
            <Box fontSize="xs" color="gray.600" mt="5px">
              created at {data?.created_at.slice(0,10)}
            </Box>
          </Box>

          <Button
            type="submit"
            colorScheme="blue"
            loading={isUpdating}
            disabled={newName.trim() === data?.name || isUpdating}
            display="none"
          >
            Update Name
          </Button>
        </Box>
        <Box mr="0px" mt="3px">
          <Box>
            <Button
              aria-label="Create New Picker"
              colorScheme="green"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                window.open(`/api/v1/feeds/${data?.external_id}.xml`, '_blank');
              }}
              size="xs"
              borderColor="white"
              borderWidth="1px"
              color="white"
              _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
              mt="10"
              mr="2"
            >
              <FiRss />
            </Button>
            <Button
              aria-label="Create New Picker"
              colorScheme="green"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                window.location.href = `/feeds/${data?.external_id}`;
              }}
              size="xs"
              borderColor="white"
              borderWidth="1px"
              color="white"
              _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
              mt="10"
              mr="0"
            >
              <FiList />
            </Button>
          </Box>
        </Box>
      </Flex>

      <Flex justifyContent="space-between" alignItems="flex-start" pt={6}>
        <Box>
          <Heading as="h2" size="lg">
            Pickers ({pickers.length})
          </Heading>
        </Box>
        <Box>
          <Button
            aria-label="Create New Picker"
            colorScheme="green"
            onClick={onOpenPickerModal}
            size="xs"
            borderColor="white"
            borderWidth="2px"
            color="white"
            _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
            mt="-10px"
          >
            <FiPlus />
          </Button>
        </Box>
      </Flex>
      <Flex justifyContent="space-between" alignItems="flex-start" pt={6} width="100%">
        <Box width="100%">
          <Accordion.Root collapsible defaultValue={["b"]}>
            {pickers.map((picker) => (
              <Accordion.Item key={picker.external_id} value={picker.external_id}>
                <Accordion.ItemTrigger>
                  <HStack flex="1" height="40px">
                    <Flex justifyContent="space-between" alignItems="flex-start" p={0} width="100%">
                      <Box>
                        <Text fontSize="md" display={{ base: 'none', md: 'table-cell' }}>
                          {picker.source_url}
                        </Text>
                        <Text fontSize="xs" display={{ md: 'none', base: 'table-cell' }}>
                          {picker.source_url.length > 40 ? `${picker.source_url.slice(0, 40)}…` : picker.source_url}
                        </Text>
                        <Text color="gray.700"> {picker.cronjob}</Text>
                      </Box>
                      <Box>
                        <Button
                          size="xs"
                          colorScheme="purple"
                          variant="outline"
                          onClick={() => handleDelete(picker.external_id)}
                          color="white"
                          _hover={{ bg: 'gray.700', color: 'red', borderColor: 'gray.700' }}
                          mr="0px"
                          mt="10px"
                        >
                          <FiTrash />
                        </Button>
                      </Box>
                    </Flex>
                  </HStack>
                  <Accordion.ItemIndicator />
                </Accordion.ItemTrigger>
                <Accordion.ItemContent>
                  <Accordion.ItemBody>
                    {picker.filters.map((filter) => (
                        <Box key={`${filter.operation}-${filter.args}`} ml="20px" color="gray.500">
                          - {filter.operation}: {filter.args}
                        </Box>
                    ))}
                  </Accordion.ItemBody>
                </Accordion.ItemContent>
              </Accordion.Item>
            ))}
          </Accordion.Root>
        </Box>
      </Flex>

      <AddPickerModal
        isOpen={isPickerModalOpen}
        onClose={onClosePickerModal}
        feedId={feedId}
        onPickerAdded={fetchData}
      />
    </Box>
  );
}
