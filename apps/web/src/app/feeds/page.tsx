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
import { Feed } from "@/types/Feed";
import {
  FiPlus,
  FiTrash,
  FiRss,
  FiSettings,
} from "react-icons/fi";
import Link from "next/link";
import { AddFeedModal } from "@/app/feeds/_components/add-feeds-modal";

function timeDeltaFromNow(dateString: string): string {
  const now = new Date();
  const date = new Date(dateString);
  const diffMs = now.getTime() - date.getTime();

  if (diffMs < 0) return "0m";

  const seconds = Math.floor(diffMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const weeks = Math.floor(days / 7);

  if (weeks > 0) return `${weeks}w`;
  if (days > 0) return `${days}d`;
  if (hours > 0) return `${hours}h`;
  if (minutes > 0) return `${minutes}m`;
  return `${seconds}s`;
}

export default function Feeds() {
  const [data, setData] = useState<Feed[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const { open: isAddModalOpen, onOpen: onAddModalOpen, onClose: onAddModalClose } = useDisclosure();
  const PAGE_SIZE = 50;
  const [page, setPage] = useState(1);
  const toast = useToast();

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const token = Cookies.get("token");
      const res = await axios.get("/api/v1/feeds", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setData(res.data.feeds);
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
    if (!window.confirm(`Are you sure you want to delete feed: ${name}?`)) {
      return;
    }

    setIsDeleting(externalId);
    try {
      const token = Cookies.get("token");
      await axios.delete(`/api/v1/feeds/${externalId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });

      toast({
        title: "Feed Deleted.",
        description: `${name} was successfully removed.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      fetchData();

    } catch (error) {
      console.error("Error deleting feed:", error);
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
      <Box ml={3} mt={{base:"-6", md:"3"}}>
        <p>Loading feeds...</p>
      </Box>
    );
  }

  const sortedFeedItems = data
  ?.slice()
  .sort((a, b) => a.name.localeCompare(b.name)) ?? [];
  const totalItems = sortedFeedItems.length;
  const paginatedItems = sortedFeedItems.slice(
    (page - 1) * PAGE_SIZE,
    page * PAGE_SIZE
  );

  return (
    <Box p={2} mt={{base:"-9", md:"5"}}>

      {/* HEADER AND CREATE FEED BUTTON */}
      <Flex
        justifyContent="space-between"
        alignItems="center"
        mb={6}
      >
        <Heading as="h1" size="xl" color='#b893c1'>
          Feeds
        </Heading>

        <Button
          colorScheme="blue"
          onClick={onAddModalOpen}
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
        mt={0}
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
            <Table.ColumnHeader bg="gray.700" color='white'># FEED ITEMS</Table.ColumnHeader>
            <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>LAST UPDATE</Table.ColumnHeader>
            <Table.ColumnHeader bg="gray.700" color='white' textAlign="center">ACTIONS</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>

        <Table.Body>
          {paginatedItems.map((item: Feed) => (
            <Table.Row key={item.external_id} cursor="pointer" _hover={{ bg: 'gray.800', color: '#AC7DBA' }}>
              <Table.Cell width={{ base: "50%", md: "60%" }}>
                <Link href={`/feeds/${item.external_id}`} passHref legacyBehavior>
                  <Box>
                    <Box fontWeight="bold">{item.name}</Box>
                  </Box>
                </Link>
              </Table.Cell>

              <Table.Cell width={{ base: "30%", md: "15%" }}>
                <Link href={`/feeds/${item.external_id}`} passHref legacyBehavior>
                  <Box>
                    <Box fontWeight="bold">{item.number_of_feed_items}</Box>
                    <Box
                      fontSize="xs"
                      color="gray.500"
                      mt={0.5}
                      display={{ base: 'block', md: 'none' }}
                    >
                      <Flex align="center" gap={1}>
                        {timeDeltaFromNow(item.latest_item_datetime as string)} ago
                      </Flex>
                    </Box>
                  </Box>
                </Link>
              </Table.Cell>

              <Table.Cell display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "15%" }}>
                <Link href={`/feeds/${item.external_id}`} passHref legacyBehavior>
                  <Box fontWeight="bold">{timeDeltaFromNow(item.latest_item_datetime as string)} ago</Box>
                </Link>
              </Table.Cell>

              <Table.Cell textAlign="center" width={{ base: "20%", md: "10%" }}>
                <Box
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >

                  <Button
                    aria-label={`Delete ${item.name}`}
                    size="xs"
                    colorScheme="red"
                    color="white"
                    _hover={{ bg: 'gray.700', color: '#7DCDE8' }}
                    variant="ghost"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      window.location.href = `/feeds/${item.external_id}/edit`;
                    }}
                    loading={isDeleting === item.external_id}
                  >
                    <FiSettings />
                  </Button>

                  <Button
                    aria-label={`Delete ${item.name}`}
                    size="xs"
                    colorScheme="red"
                    color="white"
                    _hover={{ bg: 'gray.700', color: 'red' }}
                    variant="ghost"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleDelete(item.external_id, item.name);
                    }}
                    loading={isDeleting === item.external_id}
                  >
                    <FiTrash />
                  </Button>

                  <Button
                    aria-label={`Download RSS for ${item.name}`}
                    size="xs"
                    colorScheme="blue"
                    color="white"
                    _hover={{ bg: 'gray.700', color: '#AC7DBA' }}
                    variant="ghost"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      window.open(`/api/v1/feeds/${item.external_id}.xml`, '_blank');
                    }}
                    ml={0}
                  >
                    <FiRss />
                  </Button>
                </Box>
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

      <AddFeedModal
        isOpen={isAddModalOpen}
        onClose={onAddModalClose}
        onFeedAdded={fetchData}
        isCentered
      />

    </Box>
  )
}
