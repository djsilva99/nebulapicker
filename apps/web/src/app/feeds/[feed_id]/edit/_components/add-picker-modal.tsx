"use client";

import {
  Box,
  Input,
  Button,
  Flex,
  Stack,
  Text,
  Spinner,
} from '@chakra-ui/react';

import { useToast } from "@chakra-ui/toast";
import { Select } from "@chakra-ui/select";
import {
  FormControl,
  FormLabel
} from "@chakra-ui/form-control";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalCloseButton,
  ModalBody,
  ModalFooter
} from "@chakra-ui/modal";
import { FiPlus, FiTrash, FiChevronDown } from "react-icons/fi";
import { Source } from '@/types/Source';
import { PickerFilter } from '@/types/Feed';

import axios from 'axios';
import Cookies from "js-cookie";
import { useEffect, useState } from 'react';


interface AddPickerModalProps {
  isOpen: boolean;
  onClose: () => void;
  feedId: string;
  onPickerAdded: () => void;
}

const initialFilter: PickerFilter = {
    operation: 'title_contains',
    args: "['', 1]",
};

export const AddPickerModal: React.FC<AddPickerModalProps> = (
  { isOpen, onClose, feedId, onPickerAdded }
) => {
  const [cronjob, setCronjob] = useState('* * * * *');
  const [sourceUrl, setSourceUrl] = useState('');
  const [filters, setFilters] = useState<PickerFilter[]>([initialFilter]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [urlOptions, setUrlOptions] = useState<Source[]>([]);
  const [loadingUrls, setLoadingUrls] = useState(false);
  const [urlError, setUrlError] = useState<string | null>(null);
  const toast = useToast();

  useEffect(() => {
    if (isOpen) {
      setCronjob("* * * * *");
      setSourceUrl("");
      setFilters([{ operation: "title_contains", args: "['', 1]" }]);

      const fetchUrls = async () => {
        setLoadingUrls(true);
        setUrlError(null);
        try {
          const token = Cookies.get("token");
          const response = await axios.get("/api/v1/sources", {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          const sources = Array.isArray(response.data)
            ? response.data
            : Array.isArray(response.data?.sources)
            ? response.data.sources
            : [];
          setUrlOptions(sources);
        } catch (error: unknown) {
          console.error("Error fetching URLs:", error);
          setUrlError("Failed to load URL options");
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
          setLoadingUrls(false);
        }
      };

      fetchUrls();
    }
  }, [isOpen, setCronjob, setSourceUrl, setFilters]);

  const handleFilterChange = (
    index: number, field: keyof PickerFilter, value: string
  ) => {
    const newFilters = [...filters];
    newFilters[index][field] = value;
    setFilters(newFilters);
  };

  const handleAddFilterField = () => {
    setFilters([
      ...filters,
      { operation: 'title_contains', args: "['', 1]" }
    ]);
  };

  const handleRemoveFilterField = (index: number) => {
    setFilters(filters.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    if (!sourceUrl.trim()) {
      toast(
        {
          title: "Error",
          description: "Source URL is required.",
          status: "warning",
          duration: 3000
        }
      );
      setIsSubmitting(false);
      return;
    }
    try {
      const pickerPayload = {
        cronjob,
        source_url: sourceUrl,
        filters,
        feed_external_id: feedId,
      };
      const token = Cookies.get("token");
      await axios.post("/api/v1/pickers", pickerPayload, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      toast(
        {
          title: "Picker Created",
          description: "A new picker was successfully created.",
          status: "success",
          duration: 3000,
          isClosable: true
        }
      );
      onPickerAdded();
      onClose();
    } catch (error) {
      toast(
        {
          title: "Error",
          description: "Failed to create picker.",
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
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered size="2xl">
      <ModalOverlay
        bg="gray.700"
        backdropFilter="blur(4px)"
      />
      <ModalContent
        maxH="80vh"
        top="100px"
        width={{ base: "90%", md: "40%" }}
        maxW="1800px"
        mx="auto"
        bg="#161519"
        border="2px solid"
        borderColor="white"
        borderRadius="md"
        as="form"
        onSubmit={handleSubmit}
      >
        <ModalCloseButton
          color="white"
          position="absolute"
          top="20px"
          right="20px"
          _hover={{ bg: 'gray.700', color: '#AC7DBA'}}
          cursor="pointer"
        />
        <ModalBody p={30} overflowY="auto" >
          <FormControl isRequired mt="15px">
            {loadingUrls ? (
              <Spinner size="sm" />
            ) : urlError ? (
              <Text color="red.500">{urlError}</Text>
            ) : (
              <>
                <FormLabel>Source</FormLabel>
                <Select
                  bg='#453262'
                  placeholder="Select a source URL"
                  value={sourceUrl}
                  onChange={(e) => setSourceUrl(e.target.value)}
                  h="38px"
                  borderRadius="xl"
                  borderWidth="1px"
                  pl={4}
                  pr={10}
                  icon={<FiChevronDown />}
                  iconColor="white"
                  appearance="none"
                  w="100%"
                  minW="0"
                  sx={{
                    width: '100 !important',
                    'select, &': { width: '100% !important' },
                    boxSizing: 'border-box',
                  }}
                >
                  {urlOptions.map((src) => (
                    <option key={src.external_id} value={src.url}>
                      {src.name} — {src.url}
                    </option>
                  ))}
                </Select>
              </>
            )}

          </FormControl>
          <FormControl mt="15px">
            <FormLabel>Cron Job Schedule</FormLabel>
            <Input
              bg="gray.800"
              value={cronjob}
              onChange={(e) => setCronjob(e.target.value)}
              placeholder="e.g., * * * * *"
            />
          </FormControl>

          <Flex justifyContent="space-between" alignItems="center" mt="30px">
            <FormLabel mb={0} fontWeight="bold">
              Filters ({filters.length})
            </FormLabel>
            <Button
              size="sm"
              colorScheme="green"
              mb="10px"
              aria-label="Add new filter field"
              borderColor="white"
              borderWidth="1px"
              onClick={handleAddFilterField}
              _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
            >
              <FiPlus />
            </Button>
          </Flex>

          <Stack>
            {filters.map((filter, index) => (
              <Flex key={index} p={3} borderWidth="0px" borderRadius="xl" alignItems="center" gap={10}>
                <Box width="47.5%">
                  <FormControl>
                    <FormLabel fontSize="sm" mb={1}>Operation</FormLabel>
                    <Select
                      bg='#453262'
                      value={filter.operation}
                      onChange={(e) => handleFilterChange(index, 'operation', e.target.value)}
                      h="38px"
                      borderRadius="xl"
                      borderWidth="1px"
                      p={2}
                      appearance="none"
                      w="100%"
                      minW="0"
                      sx={{
                        width: '100 !important',
                        'select, &': { width: '100% !important' },
                        boxSizing: 'border-box',
                      }}
                    >
                      <option value="identity">
                        identity
                      </option>
                      <option value="title_contains">
                        title_contains
                      </option>
                      <option value="description_contains">
                        description_contains
                      </option>
                      <option value="title_does_not_contain">
                        title_does_not_contain
                      </option>
                      <option value="description_does_not_contain">
                        description_does_not_contain
                      </option>
                      <option value="link_contains">
                        link_contains
                      </option>
                      <option value="link_does_not_contain">
                        link_does_not_contain
                      </option>
                    </Select>
                  </FormControl>
                </Box>

                <Box flex="47.5%">
                  <FormControl flex="3" mt="-5px">
                    <FormLabel fontSize="sm" mb={1}>
                      Args (JSON String)
                    </FormLabel>
                    <Input
                      bg="gray.800"
                      value={filter.args as string}
                      onChange={(e) => handleFilterChange(index, 'args', e.target.value)}
                      placeholder="e.g., ['spacex', 1]"
                      size="sm"
                    />
                  </FormControl>
                </Box>

                <Box flex="5%" display="flex" justifyContent="center" alignItems="center">
                  <Button
                    color="white"
                    ml="-6"
                    cursor="pointer"
                    onClick={() => handleRemoveFilterField(index)}
                    size="sm"
                    mt={5}
                    _hover={{ bg: 'gray.700', color: 'red', borderColor: 'gray.700' }}
                  >
                    <FiTrash/>
                  </Button>
                </Box>
              </Flex>
            ))}
          </Stack>
        </ModalBody>

        <ModalFooter>
          <Button
            colorScheme="blue"
            type="submit"
            loading={isSubmitting}
            _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
            mb="30px"
            mr="30px"
            borderColor="white"
          >
            Create Picker
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
