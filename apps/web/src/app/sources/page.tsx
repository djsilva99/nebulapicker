"use client";

import {
  Table,
  Heading,
  Box,
  Button,
  Flex,
  useDisclosure,
  Pagination
} from "@chakra-ui/react";
import { useToast } from "@chakra-ui/toast";
import { useState, useEffect } from "react";
import axios from "axios";
import Cookies from "js-cookie";
import { Source } from "@/types/Source";
import { FiPlus, FiTrash } from "react-icons/fi";
import { AddSourceModal } from "@/app/sources/_components/add-source-modal"


export default function Sources() {
  const [data, setData] = useState<Source[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const { open, onOpen, onClose } = useDisclosure();
  const PAGE_SIZE = 50;
  const [page, setPage] = useState(1);
  const toast = useToast();

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const token = Cookies.get("token");
      const res = await axios.get("/api/v1/sources", {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });
      setData(res.data.sources);
    } catch (error: unknown) {
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
  }, []);

  const handleDelete = async (externalId: string, name: string) => {
    if (!window.confirm(`Are you sure you want to delete source: ${name}?`)) {
      return;
    }

    setIsDeleting(externalId);
    try {
      const token = Cookies.get("token");
      await axios.delete(`/api/v1/sources/${externalId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      })

      toast({
        title: "Source Deleted.",
        description: `${name} was successfully removed.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      fetchData();

    } catch (error: unknown) {
      toast({
        title: "Error.",
        description: `Failed to delete ${name}.`,
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
    } finally {
      setIsDeleting(null);
    }
  };

  if (isLoading) {
    return (
      <Box ml={3} mt={{base:"-6", md:"3"}}>
        <p>Loading sources...</p>
      </Box>
    );
  }

  const sortedSourceItems = data
  ?.slice()
  .sort((a, b) => a.name.localeCompare(b.name)) ?? [];
  const totalItems = sortedSourceItems.length;
  const paginatedItems = sortedSourceItems.slice(
    (page - 1) * PAGE_SIZE,
    page * PAGE_SIZE
  );

  return (
    <Box p={2} mt={{base:"-9", md:"5"}}>

      {/* HEADER + CREATE SOURCE BUTTON */}
      <Flex
        justifyContent="space-between"
        alignItems="center"
        mb={6}
      >
        <Heading as="h1" size="xl" color='#b893c1'>
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

      <Flex
        justify="center"
        align="center"
        px={2}
        mb={4}
        fontSize="sm"
        color="gray.500"
      >
        Showing {(page - 1) * PAGE_SIZE + 1}–
        {Math.min(page * PAGE_SIZE, totalItems)} of {totalItems}
      </Flex>

      {/* TABLE */}
      <Table.Root size="sm" variant="outline">
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader bg="gray.700" color='white'>NAME</Table.ColumnHeader>
            <Table.ColumnHeader bg="gray.700" color='white' textAlign="start" display={{ base: 'none', md: 'table-cell' }}>URL</Table.ColumnHeader>
            <Table.ColumnHeader bg="gray.700" color='white' textAlign="center">ACTIONS</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>

        <Table.Body>
          {paginatedItems.map((item: Source) => (
            <Table.Row key={item.external_id} cursor="pointer" _hover={{ bg: 'gray.800', color: '#AC7DBA' }}>
              <Table.Cell width={{ base: "95%", md: "45%" }}>
                <a href={`${item.url}`} target="_blank" rel="noopener noreferrer">
                  <Box>
                    <Box fontWeight="bold">{item.name}</Box>
                  </Box>
                </a>
                  <Box
                    fontSize="xs"
                    color="gray.500"
                    mt={0.5}
                    display={{ base: 'block', md: 'none' }}
                  >
                <a href={`${item.url}`} target="_blank" rel="noopener noreferrer">
                  {item.url.length > 40 ? `${item.url.slice(0, 40)}…` : item.url}
                </a>
                  </Box>
              </Table.Cell>

              <Table.Cell textAlign="start" display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "45%" }}>
                <a href={`${item.url}`} target="_blank" rel="noopener noreferrer">
                  {item.url}
                </a>
              </Table.Cell>
              <Table.Cell textAlign="center" width={{ base: "5%", md: "5%" }}>
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

      <Flex
        justify="center"
        align="center"
        mt={4}
        px={2}
        mb={4}
        fontSize="sm"
        color="gray.500"
      >
        Showing {(page - 1) * PAGE_SIZE + 1}–
        {Math.min(page * PAGE_SIZE, totalItems)} of {totalItems}
      </Flex>

      <Flex justify="center" align="center" mt={4} mb={4}>
        <Pagination.Root
          count={totalItems}
          pageSize={PAGE_SIZE}
          page={page}
          onPageChange={(details) => setPage(details.page)}
        >
          <Pagination.Items
            render={(item) => (
              <Pagination.Item
                key={item.value}
                value={item.value}
                type={item.type}
                asChild
              >
                <Button
                  size="xs"
                  color={item.type === "page" && item.value === page ? "white" : "white"}
                  bg={item.type === "page" && item.value === page ? "#6b4078" : "transparent"}
                  variant="outline"
                  m={1}
                  _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
                >
                  {item.type === "page" ? item.value : "…"}
                </Button>
              </Pagination.Item>
            )}
          />
        </Pagination.Root>
      </Flex>

      {/* MODAL */}
      <AddSourceModal
        isOpen={open}
        onClose={onClose}
        onSourceAdded={fetchData}
        isCentered
      />
    </Box>
  )
}
