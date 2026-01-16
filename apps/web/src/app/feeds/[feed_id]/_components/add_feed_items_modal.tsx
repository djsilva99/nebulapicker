"use client";

import { format } from "date-fns";
import {
  Button,
  Input,
  Box
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

import { Text } from "@chakra-ui/react";
import Calendar from 'react-calendar';
import React from 'react';

type CalendarValue = Date | [Date | null, Date | null] | null;

interface NewFeedItem {
  title: string;
  description: string;
  link: string;
	content: string;
  created_at?: string;
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

const DatePickerWithCalendar: React.FC<DatePickerProps> = ({ formData, setFormData }) => {
  const dateValue: Date | null = formData.created_at
    ? new Date(formData.created_at)
    : null;

  const handleDateChange = (value: CalendarValue, event: React.MouseEvent<HTMLButtonElement, MouseEvent> | undefined) => {
    const selectedValue = value as Date | Date[] | null;

    const date: Date | null = Array.isArray(selectedValue)
      ? selectedValue[0]
      : (selectedValue as Date | null);

    setFormData((prevData: NewFeedItem) => ({
      ...prevData,
      created_at: date ? date.toISOString() : "",
    }));
  };

  return (
    <div className="custom-calendar-container">
      <Box
        bg="gray.700"
        borderColor="white"
        borderWidth="1px"
        borderRadius="md"
        p="10px"
      >
        <Calendar
          onChange={handleDateChange}
          value={dateValue}
          view="month"
          selectRange={false}
          showNavigation={true}
          maxDetail="month"
          prevLabel={
            <Button ml="10px" mr="10px" bg="gray.700">&lt;</Button>
          }
          nextLabel={
            <Button ml="10px" mr="10px" bg="gray.700">&gt;</Button>
          }
          prev2Label={<Button bg="gray.700">&laquo;</Button>}
          next2Label={<Button bg="gray.700">&raquo;</Button>}
        />
      </Box>
    </div>
  );
};

export const AddFeedItemModal: React.FC<AddFeedModalProps> = (
  { externalFeedId, isOpen, onClose, onFeedAdded, isCentered }
) => {
  const [formData, setFormData] = useState<NewFeedItem>(
    { title: "", description: "", link: "", content: "" }
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const toast = useToast();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    if (!formData.title) {
      toast({
        title: "Validation Error.",
        description: "Title is required.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      setIsSubmitting(false);
      return;
    }

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

    if (!formData.description) {
      toast({
        title: "Validation Error.",
        description: "Description is required.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      setIsSubmitting(false);
      return;
    }

    try {
      await axios.post(`/api/v1/feeds/${externalFeedId}/feed_items`, formData);
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
        left="35%"
        width="30%"
        maxW="1800px"
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
          <FormControl isRequired mb={4}>
            <FormLabel color="white">Link</FormLabel>
            <Input
              name="link"
              placeholder="Url"
              value={formData.link}
              onChange={handleChange}
              bg="gray.700"
              color="white"
              _placeholder={{ color: "gray.400" }}
            />
            <FormLabel color="white" mt={10}>Title</FormLabel>
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
            <FormLabel color="white" mt={10}>Timestamp</FormLabel>
            <Box position="relative" color="white">
              <DatePickerWithCalendar formData={formData} setFormData={setFormData}/>
            </Box>
            {formData.created_at && (
              <Text color="gray.400" fontSize="sm" mt={2}>
                {format(new Date(formData.created_at), "PPPp")}
              </Text>
            )}
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
