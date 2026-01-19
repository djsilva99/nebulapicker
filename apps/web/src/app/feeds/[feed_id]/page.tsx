"use client";

import {
  Table,
  Heading,
  Box,
  Flex,
  Button,
  useDisclosure,
  Link,
  Image,
  Spacer
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import axios from "axios";
import Cookies from "js-cookie";
import { Feed, FeedItem } from "@/types/Feed";
import { useParams } from 'next/navigation';
import { FiRss, FiSettings, FiTrash, FiPlus, FiGlobe, FiClock } from "react-icons/fi";
import { useToast } from "@chakra-ui/toast";
import { AddFeedItemModal } from "./_components/add_feed_items_modal";


const normalizeUrl = (url: string) => {
  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    return "https://" + url;
  }
  return url;
};

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


export default function FeedPage() {
  const useWallabagExtractor = process.env.NEXT_PUBLIC_USE_WALLABAG_EXTRACTOR === "true";
  console.log(useWallabagExtractor)
  const params = useParams();
  const feedId = params.feed_id as string;

  const [data, setData] = useState<Feed>();
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const { open, onOpen, onClose } = useDisclosure();

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

  if (isLoading) {
    return (
      <Box p={6}>
        <p>Loading feed items...</p>
      </Box>
    );
  }

  const handleDelete = async (externalId: string, feedExternalId: string) => {
    if (typeof window !== 'undefined' && !window.confirm(`Are you sure you want to delete feed item: ${feedExternalId}?`)) {
      return;
    }

    setIsDeleting(feedExternalId);
    try {
      const token = Cookies.get("token");
      await axios.delete(`/api/v1/feeds/${externalId}/feed_items/${feedExternalId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });

      toast({
        title: "Feed Item Deleted.",
        description: `feed item ${feedExternalId} was successfully removed.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      fetchData();

    } catch (error: unknown) {
      console.error("Error deleting feed item:", error);
      toast({
        title: "Error.",
        description: `Failed to delete feed item ${feedExternalId}.`,
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

  return (
    <Box p={2}>

      {/* HEADER */}
      <Flex
        justifyContent="space-between"
        alignItems="center"
        mb={6}
      >
        <Heading as="h1" size="lg">
          {data?.name} 
        </Heading>
        <Box mr="0px">
          <Box>
            <Button
              aria-label="Create New Feed Item"
              colorScheme="green"
              onClick={onOpen}
              size="xs"
              borderColor="white"
              borderWidth="1px"
              color="white"
              _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
              mr="2"
            >
              <FiPlus />
            </Button>
            <Button
              aria-label="Create New Picker"
              colorScheme="green"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                window.location.href = `/feeds/${data?.external_id}/edit`;
              }}
              size="xs"
              borderColor="white"
              borderWidth="1px"
              color="white"
              _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
              mr="2"
            >
              <FiSettings />
            </Button>

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
            >
              <FiRss />
            </Button>
          </Box>
        </Box>
      </Flex>

      {/* TABLE */}
      {useWallabagExtractor && (
        <Table.Root size="sm" variant="outline">
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeader bg="gray.700" color='white'>TITLE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>SOURCE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>DATE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}><FiClock/></Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>ACTIONS</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>

          <Table.Body>
          {data?.feed_items?.slice().sort(
            (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          ).map((item: FeedItem) => (
            <Table.Row
              key={item.external_id}
              cursor="pointer"
              color="gray.400"
              _hover={{ bg: 'gray.800', color: '#AC7DBA' }}
            >
              <Table.Cell
                borderLeft="none"
                borderRight="none"
                cursor="pointer"
                width={{ base: "100%", md: "60%" }}
                color="gray.400"
                role="group"
                _hover={{ bg: 'gray.800', color: '#AC7DBA' }}
              >
                <Link href={`/feeds/${feedId}/feed_items/${item.external_id}`} cursor="pointer"
                  color="gray.400"
                  _hover={{ bg: 'gray.800', color: '#AC7DBA' }}>
                  <Box>
                    <Flex align="center" gap={3}>
                      <Box
                        width="80px"
                        height="60px"
                        bg="gray.900"
                        overflow="hidden"
                        flexShrink={0}
                      >
                        <Image
                          src={item.image_url ?? "/nebulapicker.png"}
                          width="100%"
                          height="100%"
                          objectFit="contain"
                          pointerEvents="none"
                        />
                      </Box>
                      <Box fontWeight="medium" color="#7DCDE8">
                        {item.title}
                      </Box>
                    </Flex>
                  </Box>
                </Link>
                <Box
                  fontSize="xs"
                  color="gray.500"
                  mt={-0.5}
                  display={{ base: 'block', md: 'none' }}
                >
                  <Flex align="center" gap={1}>
                    {item.author.length > 17 ? `${item.author.slice(0, 17)}…` : item.author} &nbsp;&nbsp;
                    {timeDeltaFromNow(item.created_at)} ago &nbsp;&nbsp;
                    <FiClock/> {item.reading_time}m
                    <Spacer/>
                    <Box minW="80px">
                      <Button
                        aria-label={`Go to ${item.link}`}
                        size="xs"
                        colorScheme="red"
                        color="white"
                        _hover={{ bg: 'gray.700', color: '#AC7DBA' }}
                        variant="ghost"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          window.open(item.link, '_blank');
                        }}
                        loading={isDeleting === item.external_id}
                      >
                        <FiGlobe/>
                      </Button>
                      <Button
                        aria-label={`Delete ${item.title}`}
                        size="xs"
                        colorScheme="red"
                        color="white"
                        _hover={{ bg: 'gray.700', color: 'red' }}
                        variant="ghost"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleDelete(data?.external_id, item.external_id);
                        }}
                        loading={isDeleting === item.external_id}
                      >
                        <FiTrash/>
                      </Button>
                    </Box>
                  </Flex>
                </Box>
              </Table.Cell>
              <Table.Cell borderLeft="none" borderRight="none" display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "15%" }}>
                <Link href={`/feeds/${feedId}/feed_items/${item.external_id}`} cursor="pointer"
                  color="gray.400"
                  _hover={{ bg: 'gray.800', color: '#AC7DBA' }}>
                  <Box>{item.author}</Box>
                </Link>
              </Table.Cell>

              <Table.Cell borderLeft="none" borderRight="none" display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "10%" }}>
                <Link href={`/feeds/${feedId}/feed_items/${item.external_id}`} cursor="pointer"
                  color="gray.400"
                  _hover={{ bg: 'gray.800', color: '#AC7DBA' }}>
                  <Box>{timeDeltaFromNow(item.created_at)} ago</Box>
                </Link>
              </Table.Cell>

              <Table.Cell borderLeft="none" borderRight="none" display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "5%" }}>
                <Link href={`/feeds/${feedId}/feed_items/${item.external_id}`} cursor="pointer"
                  color="gray.400"
                  _hover={{ bg: 'gray.800', color: '#AC7DBA' }}>
                  <Box>{item.reading_time}m</Box>
                </Link>
              </Table.Cell>

              <Table.Cell borderLeft="none" borderRight="none" display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "10%" }}>
                <Box minW="80px">
                  <Button
                    aria-label={`Go to ${item.link}`}
                    size="xs"
                    colorScheme="red"
                    color="white"
                    _hover={{ bg: 'gray.700', color: '#AC7DBA' }}
                    variant="ghost"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      window.open(item.link, '_blank');
                    }}
                    loading={isDeleting === item.external_id}
                  >
                    <FiGlobe />
                  </Button>
                  <Button
                    aria-label={`Delete ${item.title}`}
                    size="xs"
                    colorScheme="red"
                    color="white"
                    _hover={{ bg: 'gray.700', color: 'red' }}
                    variant="ghost"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleDelete(data?.external_id, item.external_id);
                    }}
                    loading={isDeleting === item.external_id}
                  >
                    <FiTrash />
                  </Button>
                </Box>
              </Table.Cell>
            </Table.Row>
          ))}
          </Table.Body>
        </Table.Root>
      )}

      {!useWallabagExtractor && (
        <Table.Root size="sm" variant="outline">
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeader bg="gray.700" color='white'>TITLE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>SOURCE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>DATE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white'>ACTIONS</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>

          <Table.Body>
          {data?.feed_items?.slice().sort(
              (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          ).map((item: FeedItem) => (
            <Table.Row
              key={item.external_id}
              cursor="pointer"
              color="gray.400"
              _hover={{ bg: 'gray.800', color: '#AC7DBA' }}
            >
              <Table.Cell borderLeft="none" borderRight="none" cursor="pointer" width={{ base: "85%", md: "60%" }}
                color="gray.400"
                _hover={{ bg: 'gray.800', color: '#AC7DBA' }}>
                <a href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  color="gray.400"
                >
                  <Box>
                    <Box fontWeight="medium" color="#7DCDE8">
                      {item.title}
                    </Box>
                    <Box
                      fontSize="xs"
                      color="gray.500"
                      mt={0.5}
                      display={{ base: 'block', md: 'none' }}
                    >
                      <Flex align="center" gap={1}>
                        {item.author} &nbsp;&nbsp; {timeDeltaFromNow(item.created_at)} ago
                      </Flex>
                    </Box>
                  </Box>
                </a>
              </Table.Cell>
              <Table.Cell borderLeft="none" borderRight="none" display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "15%" }}>
                <a href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  color="gray.400"
                >
                  <Box>{item.author}</Box>
                </a>
              </Table.Cell>

              <Table.Cell borderLeft="none" borderRight="none" display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "10%" }}>
                <a href={item.link}
                  color="gray.400"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Box>{timeDeltaFromNow(item.created_at)} ago</Box>
                </a>
              </Table.Cell>

              <Table.Cell borderLeft="none" borderRight="none" width={{ base: "20%", md: "10%" }}>
                <Box minW="40px">
                  <Button
                    aria-label={`Delete ${item.title}`}
                    size="xs"
                    colorScheme="red"
                    color="white"
                    _hover={{ bg: 'gray.700', color: 'red' }}
                    variant="ghost"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleDelete(data?.external_id, item.external_id);
                    }}
                    loading={isDeleting === item.external_id}
                  >
                    <FiTrash />
                  </Button>
                </Box>
              </Table.Cell>
            </Table.Row>
          ))}
          </Table.Body>
        </Table.Root>
      )}

      <AddFeedItemModal
        externalFeedId={data?.external_id as string}
        isOpen={open}
        onClose={onClose}
        onFeedAdded={fetchData}
        isCentered
      />
    </Box>
  )
}
