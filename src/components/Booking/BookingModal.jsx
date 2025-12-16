import React, { useState } from "react";
import PropTypes from "prop-types";
import {
  Modal,
  Box,
  Text,
  Button,
  Group,
  Stack,
  Loader,
  Alert,
  Badge,
  Divider,
} from "@mantine/core";
import {
  IconCheck,
  IconAlertCircle,
  IconCar,
  IconTicket,
  IconCalendar,
} from "@tabler/icons-react";
import { bookServiceAPI } from "../../apis/itineraryService";
import useItineraryStore from "../../stores/useItineraryStore";

const BookingModal = ({ opened, onClose, stop, dayIndex, serviceType }) => {
  const [isBooking, setIsBooking] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const { bookStop } = useItineraryStore();

  const getServiceIcon = () => {
    switch (serviceType) {
      case "grab":
        return <IconCar size={24} />;
      case "ticket":
        return <IconTicket size={24} />;
      case "reservation":
        return <IconCalendar size={24} />;
      default:
        return <IconCheck size={24} />;
    }
  };

  const getServiceTitle = () => {
    switch (serviceType) {
      case "grab":
        return "Book Grab Ride";
      case "ticket":
        return "Book Entry Ticket";
      case "reservation":
        return "Make Reservation";
      default:
        return "Book Service";
    }
  };

  const getServiceDetails = () => {
    if (serviceType === "grab" && stop?.nextTravel) {
      return {
        name: "GrabCar 4-seater",
        description: `${stop.nextTravel.duration} • ${stop.nextTravel.mode}`,
        price: stop.nextTravel.price || "TBD",
      };
    }

    if (serviceType === "ticket" && stop?.bookingDetails) {
      return {
        name: stop.destination?.name || "Entry Ticket",
        description: stop.destination?.type || "Attraction",
        price: stop.bookingDetails.price || stop.destination?.entryFee || "TBD",
      };
    }

    if (serviceType === "reservation") {
      return {
        name: stop.destination?.name || "Reservation",
        description: stop.destination?.type || "Restaurant",
        price: "Free reservation",
      };
    }

    return {
      name: "Service",
      description: "Details",
      price: "TBD",
    };
  };

  const handleConfirmBooking = async () => {
    setIsBooking(true);
    setError(null);

    try {
      const details = getServiceDetails();

      // Call mock backend API
      await bookServiceAPI(stop.id, serviceType, details);

      // Update store
      bookStop(dayIndex, stop.id);

      setSuccess(true);

      // Auto-close after 1.5 seconds
      setTimeout(() => {
        onClose();
        // Reset states
        setSuccess(false);
        setError(null);
      }, 1500);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsBooking(false);
    }
  };

  const handleClose = () => {
    if (!isBooking) {
      onClose();
      // Reset states
      setSuccess(false);
      setError(null);
    }
  };

  const serviceDetails = getServiceDetails();

  return (
    <Modal
      opened={opened}
      onClose={handleClose}
      title={getServiceTitle()}
      centered
      size="md"
    >
      <Stack spacing="md">
        {/* Service Details */}
        <Box
          p="md"
          style={{
            backgroundColor: "var(--mantine-color-gray-0)",
            borderRadius: "var(--mantine-radius-md)",
          }}
        >
          <Group align="flex-start" spacing="md">
            <Box
              style={{
                color: "var(--mantine-color-blue-6)",
              }}
            >
              {getServiceIcon()}
            </Box>
            <Box style={{ flex: 1 }}>
              <Text size="lg" fw={700}>
                {serviceDetails.name}
              </Text>
              <Text size="sm" c="dimmed">
                {serviceDetails.description}
              </Text>
              <Badge color="blue" variant="light" mt="xs" size="lg">
                {serviceDetails.price}
              </Badge>
            </Box>
          </Group>
        </Box>

        <Divider />

        {/* Destination Info */}
        {stop?.destination && (
          <Box>
            <Text size="sm" fw={600} mb="xs">
              Destination
            </Text>
            <Group spacing="sm">
              {stop.destination.image && (
                <Box
                  w={60}
                  h={60}
                  style={{
                    borderRadius: "8px",
                    backgroundImage: `url("${stop.destination.image}")`,
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                  }}
                />
              )}
              <Box>
                <Text size="sm" fw={600}>
                  {stop.destination.name}
                </Text>
                <Text size="xs" c="dimmed">
                  {stop.time} • {stop.destination.type}
                </Text>
              </Box>
            </Group>
          </Box>
        )}

        {/* Error Alert */}
        {error && (
          <Alert
            icon={<IconAlertCircle size={16} />}
            title="Booking Failed"
            color="red"
            variant="light"
          >
            {error}
          </Alert>
        )}

        {/* Success Alert */}
        {success && (
          <Alert
            icon={<IconCheck size={16} />}
            title="Booking Confirmed!"
            color="green"
            variant="light"
          >
            Your booking has been confirmed successfully.
          </Alert>
        )}

        {/* Actions */}
        <Group position="right" mt="md">
          <Button variant="subtle" onClick={handleClose} disabled={isBooking}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirmBooking}
            loading={isBooking}
            disabled={success}
            leftIcon={success ? <IconCheck size={18} /> : undefined}
            color={success ? "green" : "blue"}
          >
            {isBooking ? "Booking..." : success ? "Booked!" : "Confirm Booking"}
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
};

BookingModal.propTypes = {
  opened: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  stop: PropTypes.object,
  dayIndex: PropTypes.number,
  serviceType: PropTypes.oneOf(["grab", "ticket", "reservation"]),
};

export default BookingModal;
