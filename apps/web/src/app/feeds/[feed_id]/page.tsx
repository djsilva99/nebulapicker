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
  Spacer,
  Pagination,
  Input,
  Switch,
} from "@chakra-ui/react";
import {
  FormControl,
  FormLabel
} from "@chakra-ui/form-control";
import { useState, useEffect, useMemo } from "react";
import axios from "axios";
import Cookies from "js-cookie";
import { Feed, FeedItem } from "@/types/Feed";
import { useParams } from "next/navigation";
import {
  FiRss,
  FiSettings,
  FiTrash,
  FiPlus,
  FiClock,
  FiSearch,
  FiGlobe,
  FiBookOpen,
  FiStar
} from "react-icons/fi";
import { FaStar } from "react-icons/fa";
import { useToast } from "@chakra-ui/toast";
import { AddFeedItemModal } from "./_components/add_feed_items_modal";
import { Text as ChakraText } from "@chakra-ui/react";


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
  const PAGE_SIZE = 20;
  const useWallabagExtractor =
    process.env.NEXT_PUBLIC_USE_WALLABAG_EXTRACTOR === "true";
  const params = useParams();
  const feedId = params.feed_id as string;
  const [data, setData] = useState<Feed>();
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const { open, onOpen, onClose } = useDisclosure();
  const [page, setPage] = useState(1);
  const feed_items_offset = (page - 1) * PAGE_SIZE;
  const [search, setSearch] = useState("");
  const [unreadItems, setUnreadItems] = useState(false);
  const [starred, setStarred] = useState(false);
  const [rssItems, setRssItems] = useState(false);
  const feedItems = data?.feed_items ?? [];
  const [totalItems, setTotalItems] = useState(0);
  const [totalUnreadItems, setTotalUnreadItems] = useState(0);
  const toast = useToast();

  // FETCH DATA
  const fetchData = async () => {

    try {
      const token = Cookies.get("token");
      const feedRes = await axios.get(`/api/v1/feeds/${feedId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        params: {
          title: search,
          only_starred_items: starred || undefined,
          only_unread_items: unreadItems || undefined,
          rss_items: rssItems || undefined,
          feed_items_limit: PAGE_SIZE,
          feed_items_offset,
        },
      });
      setData(feedRes.data);
      setTotalItems(feedRes.data.feed_items_total_count ?? 0);
      setTotalUnreadItems(feedRes.data.unread_feed_items_total_count ?? 0);

    } catch (error: unknown) {
      console.error("Error fetching data:", error);
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        Cookies.remove("token");
        window.location.href = "/login";
      }
    }
  };

  useEffect(() => {
    const loadInitial = async () => {
      await fetchData();
      setIsInitialLoading(false);
    };

    loadInitial();
  }, []);

  useEffect(() => {
    if (isInitialLoading) return;

    fetchData();
  }, [feedId, page, search, starred, unreadItems, rssItems]);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [page]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setPage(1);
    }
  };

  const handleDelete = async (externalId: string, feedExternalId: string) => {
    if (!window.confirm(`Are you sure you want to delete feed item: ${feedExternalId}?`)) {
      return;
    }

    setIsDeleting(feedExternalId);
    try {
      const token = Cookies.get("token");
      await axios.delete(
        `/api/v1/feeds/${externalId}/feed_items/${feedExternalId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast({
        title: "Feed Item Deleted.",
        description: `Feed item ${feedExternalId} was successfully removed.`,
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
    } finally {
      setIsDeleting(null);
    }
  };

  const handleCatchup = async (externalId: string) => {
    try {
      const token = Cookies.get("token");
      await axios.patch(
        `/api/v1/feeds/${externalId}/feed_items/`,
        { "read": true },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchData();
    } catch (error: unknown) {
      console.error("Error marking all as read", error);
      toast({
        title: "Error.",
        description: `Failed to mark all items as read for feed ${externalId}.`,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
    }
  };

  const handleReadItem = async (externalId: string, externalItemId: string, read: boolean) => {
    try {
      const token = Cookies.get("token");
      await axios.patch(
        `/api/v1/feeds/${externalId}/feed_items/${externalItemId}`,
        { "read": read },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchData();
    } catch (error: unknown) {
      console.error("Error marking item as read", error);
      toast({
        title: "Error.",
        description: `Failed to mark item ${externalItemId} as read for feed ${externalId}.`,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
    }
  };

    const handleStarItem = async (externalId: string, externalItemId: string, star: boolean) => {
    try {
      const token = Cookies.get("token");
      await axios.patch(
        `/api/v1/feeds/${externalId}/feed_items/${externalItemId}`,
        { "is_starred": star },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchData();
    } catch (error: unknown) {
      console.error("Error marking item as read", error);
      toast({
        title: "Error.",
        description: `Failed to mark item ${externalItemId} as read for feed ${externalId}.`,
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
    }
  };

  // LOADING
  if (isInitialLoading) {
    return (
      <Box ml={3} mt={{base:"-6", md:"3"}}>
        <p>Loading feed items...</p>
      </Box>
    );
  }

  return (
    <Box p={2} mt={{base:"-9", md:"5"}}>
      {/* HEADER */}
      <Flex justifyContent="space-between" alignItems="center" mb={6}>
        <Heading as="h1" size="xl" color='#b893c1'>
          {data?.name}
        </Heading>
        <Box mr="0px">
          <Flex>
            <Button
              aria-label="Create New Feed Item"
              colorScheme="green"
              onClick={onOpen}
              size="xs"
              borderColor="white"
              borderWidth="1px"
              color="white"
              _hover={{ bg: "gray.700", color: "#AC7DBA", borderColor: "gray.700" }}
              mr="2"
            >
              <FiPlus />
            </Button>
            <Button
              aria-label="Edit Feed"
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
              _hover={{ bg: "gray.700", color: "#AC7DBA", borderColor: "gray.700" }}
              mr="2"
            >
              <FiSettings />
            </Button>
            <Button
              aria-label="RSS Feed"
              colorScheme="green"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                window.open(`/api/v1/feeds/${data?.external_id}.xml`, "_blank");
              }}
              size="xs"
              borderColor="white"
              borderWidth="1px"
              color="white"
              _hover={{ bg: "gray.700", color: "#AC7DBA", borderColor: "gray.700" }}
            >
              <FiRss />
            </Button>
          </Flex>
        </Box>
      </Flex>

      {/* SEARCH + SWITCHES */}
      {!useWallabagExtractor && (
        <Flex mb={4} px={0} align="center" gap={0}>

          {/* SEARCH */}
          <Box
            position="relative"
            width="75%"
          >
            <Box
              position="absolute"
              top="50%"
              transform="translateY(-50%)"
              pointerEvents="none"
            >
              <FiSearch color="gray.400" />
            </Box>
            <Input
              placeholder="Search by title"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleKeyDown}
              bg="gray.900"
              borderColor="white"
              color="white"
              ps="1rem"
              _placeholder={{ color: "gray.500" }}
              _focus={{ borderColor: "#562565" }}
              borderWidth="1px"
            />
          </Box>

          <Spacer />
        
          <FormControl>
            <Flex direction="column" align="center" gap={1} mr="15px">
              <FormLabel
                htmlFor="rss_items"
                mb="0"
                fontSize="xs"
                color="gray.400"
              >
                RSS
              </FormLabel>
              <Switch.Root
                id="rss-items"
                checked={rssItems}
                onCheckedChange={(details) => {
                  setRssItems(details.checked);
                  setPage(1);
                }}
                colorPalette="purple"
              >
                <Switch.HiddenInput />
                <Switch.Control />
              </Switch.Root>
            </Flex>
          </FormControl>

        </Flex>
      )}
      {useWallabagExtractor && (
        <Flex mb={4} px={0} align="center" gap={0}>

          {/* SEARCH */}
          <Box
            position="relative"
            width="100%"
          >
            <Box
              position="absolute"
              top="50%"
              transform="translateY(-50%)"
              pointerEvents="none"
            >
              <FiSearch color="gray.400" />
            </Box>
            <Input
              placeholder="Search by title"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={handleKeyDown}
              bg="gray.900"
              borderColor="white"
              color="white"
              ps="1rem"
              _placeholder={{ color: "gray.500" }}
              _focus={{ borderColor: "#562565" }}
              borderWidth="1px"
            />
          </Box>
          <Spacer />
        </Flex>
      )}
      <Flex w="86%" mb={4} px={0} align="center" justify="space-between" ml="7%" mr="7%">

        {useWallabagExtractor && (
          <FormControl>
            <Flex direction="column" align="center" gap={1}>
              <FormLabel
                htmlFor="catchup"
                mb="0"
                fontSize="xs"
                color="gray.400"
              >
                catchup
              </FormLabel>
              <FiBookOpen style={{ cursor: 'pointer' }}
              onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  handleCatchup(data?.external_id || "");
                }}
              />
            </Flex>
          </FormControl>
        )}

        {useWallabagExtractor && (
          <FormControl>
            <Flex direction="column" align="center" gap={1}>
              <FormLabel
                htmlFor="unread-items"
                mb="0"
                fontSize="xs"
                color="gray.400"
              >
                unread
              </FormLabel>
              <Switch.Root
                id="unread-items"
                checked={unreadItems}
                onCheckedChange={(details) => {
                  setUnreadItems(details.checked);
                  setPage(1);
                }}
                colorPalette='purple'
              >
                <Switch.HiddenInput />
                <Switch.Control />
              </Switch.Root>
            </Flex>
          </FormControl>
        )}

        {(useWallabagExtractor && data?.name != "Stared") && (
          <FormControl>
            <Flex direction="column" align="center" gap={1}>
              <FormLabel
                htmlFor="last-day"
                mb="0"
                fontSize="xs"
                color="gray.400"
              >
                starred
              </FormLabel>
              <Switch.Root
                id="last-day"
                checked={starred}
                onCheckedChange={(details) => {
                  setStarred(details.checked);
                  setPage(1);
                }}
                colorPalette='purple'
              >
                <Switch.HiddenInput />
                <Switch.Control />
              </Switch.Root>
            </Flex>
          </FormControl>
        )}

        {(useWallabagExtractor && data?.name != "Stared") && (
          <FormControl>
            <Flex direction="column" align="center" gap={1}>
              <FormLabel
                htmlFor="rss_items"
                mb="0"
                fontSize="xs"
                color="gray.400"
              >
                RSS
              </FormLabel>
              <Switch.Root
                id="rss-items"
                checked={rssItems}
                onCheckedChange={(details) => {
                  setRssItems(details.checked);
                  setPage(1);
                }}
                colorPalette="purple"
              >
                <Switch.HiddenInput />
                <Switch.Control />
              </Switch.Root>
            </Flex>
          </FormControl>
        )}
      </Flex>

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
        {Math.min(page * PAGE_SIZE, totalItems)} of {totalItems} {useWallabagExtractor ? '(' + String(totalUnreadItems) + ')' : ''}
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

      {/* TABLE */}
      {useWallabagExtractor && (
        <Table.Root size="sm" variant="outline">
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>TITLE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>SOURCE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>DATE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}><FiClock/></Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>ACTIONS</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>

          <Table.Body>
          {feedItems.map((item: FeedItem) => (
            <Table.Row
              key={item.external_id}
              cursor="pointer"
              color="gray.400"
              _hover={{ bg: '#3c3652', color: '#AC7DBA' }}
            >
              <Table.Cell
                borderLeft="none"
                borderRight="none"
                cursor="pointer"
                width={{ base: "100%", md: "55%" }}
                color="gray.400"
                role="group"
                _hover={{ bg: '#3c3652', color: '#AC7DBA' }}
              >
                <Link href={`/feeds/${feedId}/feed_items/${item.external_id}`} cursor="pointer"
                  color="gray.400"
                  _hover={{ bg: 'gray.800', color: '#AC7DBA' }}>
                  <Box _hover={{ bg: '#3c3652', color: '#AC7DBA'}}>
                    <Flex align="center" gap={3}>
                      <Box
                        width="80px"
                        height="60px"
                        bg="transparent"
                        overflow="hidden"
                        flexShrink={0}
                      >
                        <Image
                          bg="transparent"
                          src={item.image_url ?? "/nebulapicker.png"}
                          width="100%"
                          height="100%"
                          objectFit="contain"
                          pointerEvents="none"
                        />
                      </Box>
                      <Box 
                        fontWeight="medium"
                        color={item.read ? "white" : '#7DCDE8'}
                      >
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
                    <Box
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleReadItem(data?.external_id || "", item.external_id, !item.read);
                      }}
                    >
                      {item.author.length > 15 ? `${item.author.slice(0, 15)}…` : item.author} &nbsp;&nbsp;
                      {timeDeltaFromNow(item.created_at)} ago &nbsp;&nbsp;
                      <Flex
                        as="span"
                        display="inline-flex"
                        alignItems="center"
                        gap="4px"
                        verticalAlign="middle"
                      >
                        <FiClock size={16}/> 
                        <ChakraText as="span" lineHeight="1">
                          {item.reading_time}m
                        </ChakraText>
                      </Flex>
                    </Box>
                    <Spacer/>
                    <Box minW="80px">
                      <Button
                        aria-label={`Go to ${item.link}`}
                        size="xs"
                        colorScheme="red"
                        color={item.is_starred ? '#AC7DBA' : "gray.500"}
                        _hover={{ bg: 'gray.700', color: '#AC7DBA' }}
                        variant="ghost"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleStarItem(data?.external_id || "", item.external_id, !item.is_starred);
                        }}
                        loading={isDeleting === item.external_id}
                      >
                        {item.is_starred ? <FaStar /> : <FiStar />}
                      </Button>
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
                          handleDelete(data?.external_id || "", item.external_id);
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
                  color={item.read ? "white" : '#7DCDE8'}
                  _hover={{ bg: '#3c3652' }}>
                  <Box>{item.author}</Box>
                </Link>
              </Table.Cell>

              <Table.Cell borderLeft="none" borderRight="none" display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "10%" }}>
                <Link href={`/feeds/${feedId}/feed_items/${item.external_id}`} cursor="pointer"
                  color={item.read ? "white" : '#7DCDE8'}
                  _hover={{ bg: '#3c3652' }}>
                  <Box>{timeDeltaFromNow(item.created_at)} ago</Box>
                </Link>
              </Table.Cell>

              <Table.Cell borderLeft="none" borderRight="none" display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "5%" }}>
                <Link href={`/feeds/${feedId}/feed_items/${item.external_id}`} cursor="pointer"
                  color={item.read ? "white" : '#7DCDE8'}
                  _hover={{ bg: '#3c3652' }}>
                  <Box>{item.reading_time}m</Box>
                </Link>
              </Table.Cell>

              <Table.Cell borderLeft="none" borderRight="none" display={{ base: 'none', md: 'table-cell' }} width={{ base: "0%", md: "15%" }}>
                <Box minW="80px">
                  <Button
                    aria-label={`Go to ${item.link}`}
                    size="xs"
                    colorScheme="red"
                    color={item.is_starred ? '#AC7DBA' : "gray.500"}
                    _hover={{ bg: 'gray.700', color: '#AC7DBA' }}
                    variant="ghost"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleStarItem(data?.external_id || "", item.external_id, !item.is_starred);
                    }}
                    loading={isDeleting === item.external_id}
                  >
                    {item.is_starred ? <FaStar /> : <FiStar />}
                  </Button>
                  <Button
                    aria-label={`Delete ${item.title}`}
                    size="xs"
                    colorScheme="red"
                    color={item.read ? "white" : '#7DCDE8'}
                    _hover={{ bg: 'gray.700', color: '#AC7DBA' }}
                    variant="ghost"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleReadItem(data?.external_id || "", item.external_id, !item.read);
                    }}
                    loading={isDeleting === item.external_id}
                  >
                    <FiBookOpen />
                  </Button>
                  <Button
                    aria-label={`Go to ${item.link}`}
                    size="xs"
                    colorScheme="red"
                    color={item.read ? "white" : '#7DCDE8'}
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
                  {useWallabagExtractor && (
                    <Button
                      aria-label={`Delete ${item.title}`}
                      size="xs"
                      colorScheme="red"
                      color={item.read ? "white" : '#7DCDE8'}
                      _hover={{ bg: 'gray.700', color: 'red' }}
                      variant="ghost"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDelete(data?.external_id || "", item.external_id);
                      }}
                      loading={isDeleting === item.external_id}
                    >
                      <FiTrash />
                    </Button>
                  )}
                  {!useWallabagExtractor && (
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
                        handleDelete(data?.external_id || "", item.external_id);
                      }}
                      loading={isDeleting === item.external_id}
                    >
                      <FiTrash />
                    </Button>
                  )}
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
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>TITLE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>SOURCE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>DATE</Table.ColumnHeader>
              <Table.ColumnHeader bg="gray.700" color='white' display={{ base: 'none', md: 'table-cell' }}>ACTIONS</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>

          <Table.Body>
          {feedItems.map((item: FeedItem) => (
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
                    <Box fontWeight="medium" color="white">
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
                  {useWallabagExtractor && (
                    <Button
                      aria-label={`Delete ${item.title}`}
                      size="xs"
                      color={item.read ? "white" : '#7DCDE8'}
                      _hover={{ bg: 'gray.700', color: 'red' }}
                      variant="ghost"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDelete(data?.external_id || "", item.external_id);
                      }}
                      loading={isDeleting === item.external_id}
                    >
                      <FiTrash />
                    </Button>
                  )}
                  {!useWallabagExtractor && (
                    <Button
                      aria-label={`Delete ${item.title}`}
                      size="xs"
                      color="white"
                      _hover={{ bg: 'gray.700', color: 'red' }}
                      variant="ghost"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDelete(data?.external_id || "", item.external_id);
                      }}
                      loading={isDeleting === item.external_id}
                    >
                      <FiTrash />
                    </Button>
                  )}
                </Box>
              </Table.Cell>
            </Table.Row>
          ))}
          </Table.Body>
        </Table.Root>
      )}

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
        {Math.min(page * PAGE_SIZE, totalItems)} of {totalItems} {useWallabagExtractor ? '(' + String(totalUnreadItems) + ')' : ''}
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

      {/* ADD ITEM MODAL */}
      <AddFeedItemModal
        externalFeedId={data?.external_id as string}
        isOpen={open}
        onClose={onClose}
        onFeedAdded={fetchData}
        isCentered
      />
    </Box>
  );
}
