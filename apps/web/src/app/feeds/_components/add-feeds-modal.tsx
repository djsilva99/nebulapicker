"use client";

import {
  Button,
  Input,
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

interface NewFeed {
  name: string;
}

interface AddFeedModalProps {
  isOpen: boolean;
  onClose: () => void;
  onFeedAdded: () => void;
  isCentered: boolean;
}

export const AddFeedModal: React.FC<AddFeedModalProps> = (
  { isOpen, onClose, onFeedAdded, isCentered }
) => {
  const [formData, setFormData] = useState<NewFeed>({ name: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const toast = useToast();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    if (!formData.name) {
      toast({
        title: "Validation Error.",
        description: "Name is required.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      setIsSubmitting(false);
      return;
    }

    try {
      await axios.post("/api/v1/feeds", formData);
      toast({
        title: "Feed Added.",
        description: `${formData.name} was successfully created.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      onFeedAdded();
      onClose();
      setFormData({ name: "" });
    } catch (error) {
      console.error("Error creating feed:", error);
      toast({
        title: "Error.",
        description: "Failed to create feed. Please try again.",
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
        top="300px"
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
            <FormLabel color="white">Feed Name</FormLabel>
            <Input
              name="name"
              placeholder="e.g., Internal Database"
              value={formData.name}
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
            _hover={{ bg: 'gray.700', color: '#AC7DBA', borderColor: 'gray.700' }}
            mb="30px"
            mr="30px"
            borderColor="white"
          >
            Create Feed
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
