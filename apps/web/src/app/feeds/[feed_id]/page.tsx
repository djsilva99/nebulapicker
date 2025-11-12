"use client";

import {
  Table,
  Heading,
  Box,
  Flex,
  Button,
  useDisclosure
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import axios from "axios";
import { Feed, FeedItem } from "@/types/Feed";
import { useParams } from 'next/navigation';
import { FiRss, FiSettings, FiTrash, FiPlus } from "react-icons/fi";
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
      const feedRes = await axios.get("/api/v1/feeds/" + feedId);
      setData(feedRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
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
        <Heading as="h1" size="xl" mb={6}>Feeds</Heading>
        <p>Loading feed items...</p>
      </Box>
    );
  }

  const handleDelete = async (externalId: string, feedExternalId: string) => {
    if (!window.confirm(`Are you sure you want to delete feed item: ${feedExternalId}?`)) {
      return;
    }

    setIsDeleting(feedExternalId);
    try {
      await axios.delete(`/api/v1/feeds/${externalId}/feed_items/${feedExternalId}`);

      toast({
        title: "Feed Item Deleted.",
        description: `feed item ${feedExternalId} was successfully removed.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      fetchData();

    } catch (error) {
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

  return (
    <Box p={6}>

      {/* HEADER */}
      <Flex
        justifyContent="space-between"
        alignItems="center"
        mb={6}
      >
        <Heading as="h1" size="xl">
          {data?.name} ({data?.feed_items?.length})
        </Heading>
        <Box mr="0px">
          <Box>
            <Button
              aria-label="Create New Feed Item"
              colorScheme="green"
              onClick={onOpen}
              size="md"
              borderColor="white"
              borderWidth="1px"
              color="white"
              _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
              mr="4"
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
              size="md"
              borderColor="white"
              borderWidth="1px"
              color="white"
              _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
              mr="4"
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
              size="md"
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
      <Table.Root size="sm" variant="outline">
        <Table.ColumnGroup>
          <Table.Column htmlWidth="70%" />
          <Table.Column htmlWidth="15%" />
          <Table.Column htmlWidth="5%" />
          <Table.Column htmlWidth="5%" />
        </Table.ColumnGroup>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader bg="gray.700" color='white'>TITLE</Table.ColumnHeader>
            <Table.ColumnHeader bg="gray.700" color='white'>AUTHOR</Table.ColumnHeader>
            <Table.ColumnHeader bg="gray.700" color='white'>DATE</Table.ColumnHeader>
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
            <Table.Cell borderLeft="none" borderRight="none">
              <a
                href={normalizeUrl(item.link)}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Box>{item.title}</Box>
              </a>
            </Table.Cell>
            <Table.Cell borderLeft="none" borderRight="none">
              <a href={normalizeUrl(item.link)}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Box>{item.author}</Box>
              </a>
            </Table.Cell>
            <Table.Cell borderLeft="none" borderRight="none">
              <a
                href={normalizeUrl(item.link)}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Box>{timeDeltaFromNow(item.created_at)}</Box>
              </a>
            </Table.Cell>

            <Table.Cell textAlign="center">
              <Box
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <Button
                  aria-label={`Delete ${item.title}`}
                  size="sm"
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
