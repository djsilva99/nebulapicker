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

interface NewSource {
  name: string;
  url: string;
}

interface AddSourceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSourceAdded: () => void;
  isCentered: boolean;
}

export const AddSourceModal: React.FC<AddSourceModalProps> = (
  { isOpen, onClose, onSourceAdded, isCentered }
) => {
  const [formData, setFormData] = useState<NewSource>({ name: "", url: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const toast = useToast();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    if (!formData.name || !formData.url) {
      toast({
        title: "Validation Error.",
        description: "Name and URL are required.",
        status: "warning",
        duration: 3000,
        isClosable: true,
      });
      setIsSubmitting(false);
      return;
    }

    try {
      await axios.post("/api/v1/sources", formData);

      toast({
        title: "Source Added.",
        description: `${formData.name} was successfully created.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      onSourceAdded();
      onClose();
      setFormData({ name: "", url: "" });
    } catch (error) {
      toast({
        title: "Error.",
        description: "Failed to create source. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered>
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
            <FormLabel color="white">Source Name</FormLabel>
            <Input
              name="name"
              placeholder="e.g., portugal_news"
              value={formData.name}
              onChange={handleChange}
              bg="gray.700"
              color="white"
              _placeholder={{ color: "gray.400" }}
            />
          </FormControl>

          <FormControl isRequired mt="15px">
            <FormLabel color="white">URL</FormLabel>
            <Input
              name="url"
              placeholder="e.g., https://www.mynewswebsite.com"
              value={formData.url}
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
            Create Source
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};
