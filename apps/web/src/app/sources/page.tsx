"use client";

import {
  Table,
  Heading,
  Box,
  Button,
  Flex,
  useDisclosure,
} from "@chakra-ui/react";
import { useToast } from "@chakra-ui/toast";
import { useState, useEffect } from "react";
import axios from "axios";
import { Source } from "@/types/Source";
import { FiPlus, FiTrash } from "react-icons/fi";
import { AddSourceModal } from "@/app/sources/_components/add-source-modal"


export default function Sources() {
  const [data, setData] = useState<Source[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const { open, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const res = await axios.get("/api/v1/sources");
      setData(res.data.sources);
    } catch (error) {
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDelete = async (externalId: string, name: string) => {
    if (!window.confirm(`Are you sure you want to delete source: ${name}?`)) {
      return;
    }

    setIsDeleting(externalId);
    try {
      await axios.delete(`/api/v1/sources/${externalId}`);

      toast({
        title: "Source Deleted.",
        description: `${name} was successfully removed.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      fetchData();

    } catch (error) {
      toast({
        title: "Error.",
        description: `Failed to delete ${name}.`,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsDeleting(null);
    }
  };

  if (isLoading) {
    return (
      <Box p={6}>
        <Heading as="h1" size="xl" mb={6}>Sources</Heading>
        <p>Loading sources...</p>
      </Box>
    );
  }

  return (
    <Box p={0}>

      {/* HEADER + CREATE SOURCE BUTTON */}
      <Flex
        justifyContent="space-between"
        alignItems="center"
        mb={6}
      >
        <Heading as="h1" size="xl">
          Sources
        </Heading>

        <Button
          colorScheme="blue"
          onClick={onOpen}
          borderColor="white"
          borderWidth="1px"
          color="white"
          size="xs"
          _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
        >
          <FiPlus />
        </Button>
      </Flex>

      {/* TABLE */}
      <Table.Root size="sm" variant="outline">
        <Table.ColumnGroup>
          <Table.Column htmlWidth="50%"/>
          <Table.Column htmlWidth="45%"/>
          <Table.Column htmlWidth="5%"/>
        </Table.ColumnGroup>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader bg="gray.700" color='white'>NAME</Table.ColumnHeader>
            <Table.ColumnHeader bg="gray.700" color='white' textAlign="start">URL</Table.ColumnHeader>
            <Table.ColumnHeader bg="gray.700" color='white' textAlign="center">ACTIONS</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>

        <Table.Body>
          {data.map((item: Source) => (
            <Table.Row key={item.external_id} cursor="pointer" _hover={{ bg: 'gray.800', color: '#AC7DBA' }}>
              <Table.Cell>
                <a href={`${item.url}`} target="_blank" rel="noopener noreferrer">
                  <Box>
                    <Box fontWeight="bold">{item.name}</Box>
                  </Box>
                </a>
              </Table.Cell>

              <Table.Cell textAlign="start">
                <a href={`${item.url}`} target="_blank" rel="noopener noreferrer">
                  {item.url}
                </a>
              </Table.Cell>
              <Table.Cell textAlign="center">
                <Button
                  aria-label={`Delete ${item.name}`}
                  size="sm"
                  colorScheme="red"
                  color="white"
                  _hover={{ bg: 'gray.700', color: 'red' }}
                  variant="ghost"
                  onClick={() => handleDelete(item.external_id, item.name)}
                  loading={isDeleting === item.external_id}
                >
                  <FiTrash />
                </Button>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>

      {/* MODAL */}
      <AddSourceModal
        isOpen={open}
        onClose={onClose}
        onSourceAdded={fetchData}
        isCentered
      />
      <Box flex="1" minH="calc(100vh - 200px)" />
    </Box>
  )
}
