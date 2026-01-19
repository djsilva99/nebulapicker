"use client";

import {
  Button,
  Input
} from "@chakra-ui/react";
import {
  FormControl,
  FormLabel
} from "@chakra-ui/form-control";
import { useToast } from "@chakra-ui/toast";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalCloseButton,
  ModalBody,
  ModalFooter
} from "@chakra-ui/modal";
import { useState } from "react";
import axios from "axios";
import Cookies from "js-cookie";

import React from 'react';

type CalendarValue = Date | [Date | null, Date | null] | null;

interface NewFeedItem {
  link: string;
  title: string;
  description: string;
	content: string;
  created_at?: string;
  image_url?: string;
}

interface AddFeedModalProps {
  externalFeedId: string;
  isOpen: boolean;
  onClose: () => void;
  onFeedAdded: () => void;
  isCentered: boolean;
}

interface DatePickerProps {
  formData: NewFeedItem;
  setFormData: React.Dispatch<React.SetStateAction<NewFeedItem>>;
}

export const AddFeedItemModal: React.FC<AddFeedModalProps> = (
  { externalFeedId, isOpen, onClose, onFeedAdded, isCentered }
) => {
  var title_label: string
  const useWallabagExtractor = process.env.NEXT_PUBLIC_USE_WALLABAG_EXTRACTOR === "true";
  if (useWallabagExtractor){
    title_label = "Title"
  } else {
    title_label = "Title*"
  }
  const [formData, setFormData] = useState<NewFeedItem>(
    { title: "", description: "", link: "", content: "", image_url: "" }
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const toast = useToast();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    if (!formData.link) {
      toast({
        title: "Validation Error.",
        description: "Link is required.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      setIsSubmitting(false);
      return;
    }

    try {
      const token = Cookies.get("token");
      await axios.post(`/api/v1/feeds/${externalFeedId}/feed_items`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      });
      toast({
        title: "Feed Item Added.",
        description: `${formData.title} was successfully created.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      onFeedAdded();
      onClose();
      setFormData({ title: "", description: "", link: "", content: "" });
    } catch (error) {
      console.error("Error creating feed item:", error);
      toast({
        title: "Error.",
        description: "Failed to create feed item. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered={isCentered}>
      <ModalOverlay
        bg="gray.700"
        backdropFilter="blur(4px)"
      />
      <ModalContent
        top="100px"
        width={{ base: "90%", md: "40%" }}
        maxW="3000px"
        mx="auto"
        bg="#161519"
        border="1px solid"
        borderColor="white"
        borderRadius="md"
        as="form"
        onSubmit={(e) => { e.preventDefault(); handleSubmit(); }}
      >
        <ModalCloseButton
          color="white"
          position="absolute"
          top="20px"
          right="20px"
          _hover={{ bg: 'gray.700', color: '#AC7DBA'}}
          cursor="pointer"
        />

        <ModalBody p={30}>
          <FormControl mb={4}>
            <FormLabel color="white">Link*</FormLabel>
            <Input
              name="link"
              placeholder="Url"
              value={formData.link}
              onChange={handleChange}
              bg="gray.700"
              color="white"
              _placeholder={{ color: "gray.400" }}
            />
            <FormLabel color="white" mt={10}>{title_label}</FormLabel>
            <Input
              name="title"
              placeholder="Title"
              value={formData.title}
              onChange={handleChange}
              bg="gray.700"
              color="white"
              _placeholder={{ color: "gray.400" }}
            />
            <FormLabel color="white" mt={10}>Description</FormLabel>
            <Input
              name="description"
              placeholder="Description"
              value={formData.description}
              onChange={handleChange}
              bg="gray.700"
              color="white"
              _placeholder={{ color: "gray.400" }}
            />
            <FormLabel color="white" mt={10}>Content</FormLabel>
            <Input
              name="content"
              placeholder="Content"
              value={formData.content}
              onChange={handleChange}
              bg="gray.700"
              color="white"
              _placeholder={{ color: "gray.400" }}
            />
            <FormLabel color="white" mt={10}>Image URL</FormLabel>
            <Input
              name="image_url"
              placeholder="Image URL"
              value={formData.image_url}
              onChange={handleChange}
              bg="gray.700"
              color="white"
              _placeholder={{ color: "gray.400" }}
            />
          </FormControl>
        </ModalBody>

        <ModalFooter>
          <Button
            colorScheme="blue"
            type="submit"
            loading={isSubmitting}
            _hover={
              { bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }
            }
            mb="30px"
            mr="30px"
            borderColor="white"
          >
            Create Feed Item
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
