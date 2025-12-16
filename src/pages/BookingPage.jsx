import React, { useState, useEffect } from "react";
import AppLayout from "../components/layout/AppLayout/AppLayout";
import BookingItemCard from "../components/Booking/BookingItemCard";
import PaymentSummary from "../components/Booking/PaymentSummary";
import OrderHeader from "../components/Booking/OrderHeader";
import ContextualToolbar from "../components/ContextualToolbar/ContextualToolbar";
import {
  Container,
  Grid,
  Stack,
  Loader,
  Alert,
  Box,
  Paper,
  Group,
  Badge,
  Button,
  Text,
} from "@mantine/core";
import { IconAlertCircle, IconShare } from "@tabler/icons-react";
import {
  pendingBookings,
  paymentMethods,
  currentOrder,
  pricingConfig,
} from "../data/mockData";
import useBookingStore from "../stores/useBookingStore";

/**
 * Booking Page - Review and confirm pending bookings
 * Displays booking items with payment summary and confirmation
 */
const BookingPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [bookings, setBookings] = useState([]);
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState(
    paymentMethods.find((m) => m.isDefault)?.id
  );
  const [isProcessing, setIsProcessing] = useState(false);

  const { confirmBooking, cancelBooking } = useBookingStore();

  // Simulate loading bookings
  useEffect(() => {
    const loadBookings = async () => {
      setIsLoading(true);
      // Simulate API call
      setTimeout(() => {
        setBookings(pendingBookings);
        setIsLoading(false);
      }, 500);
    };

    loadBookings();
  }, []);

  // Calculate pricing
  const calculatePricing = () => {
    const subtotal = bookings.reduce((sum, booking) => sum + booking.price, 0);
    const serviceFee = pricingConfig.serviceFeeFixed;
    const tax = Math.round((subtotal + serviceFee) * pricingConfig.taxRate);
    const total = subtotal + serviceFee + tax;

    return { subtotal, serviceFee, tax, total };
  };

  const pricing = calculatePricing();

  // Handle booking actions
  const handleEdit = (booking) => {
    console.log("Edit booking:", booking);
    // TODO: Implement edit modal
  };

  const handleRemove = (booking) => {
    console.log("Remove booking:", booking);
    setBookings(bookings.filter((b) => b.id !== booking.id));
    // TODO: Call API to cancel booking
  };

  const handleConfirmPayment = async () => {
    setIsProcessing(true);

    // Simulate payment processing
    setTimeout(() => {
      console.log("Payment confirmed!");
      console.log("Selected payment method:", selectedPaymentMethod);
      console.log("Total amount:", pricing.total);

      // Confirm all bookings
      bookings.forEach((booking) => {
        confirmBooking(booking.id);
      });

      setIsProcessing(false);

      // TODO: Show success modal and redirect
      alert("Booking confirmed successfully! ✓");
    }, 2000);
  };

  // Loading state
  if (isLoading) {
    return (
      <AppLayout>
        <Box
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: 16,
          }}
        >
          <Loader size="xl" />
          <Text c="dimmed">Loading your bookings...</Text>
        </Box>
      </AppLayout>
    );
  }

  // No bookings state
  if (bookings.length === 0) {
    return (
      <AppLayout>
        <Box
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 24,
          }}
        >
          <Alert
            icon={<IconAlertCircle size={16} />}
            title="No Pending Bookings"
            color="blue"
            variant="light"
            style={{ maxWidth: 400 }}
          >
            You don't have any pending bookings to review. Start planning your
            trip to add bookings!
          </Alert>
        </Box>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <Box
        style={{
          flex: 1,
          backgroundColor: "var(--mantine-color-gray-0)",
          position: "relative",
          overflow: "hidden",
          height: "100%",
        }}
      >
        {/* Top Floating Bar */}
        <Box
          pos="absolute"
          top={0}
          left={0}
          right={0}
          p="md"
          style={{ zIndex: 20, pointerEvents: "none" }}
        >
          <Group justify="space-between" align="flex-start">
            {/* View Tabs - Reusing ContextualToolbar */}
            <ContextualToolbar />

            {/* Status Badge */}
            <Paper
              shadow="sm"
              radius="lg"
              p="md"
              withBorder
              style={{
                backgroundColor: "rgba(255, 255, 255, 0.9)",
                backdropFilter: "blur(10px)",
                pointerEvents: "auto",
              }}
            >
              <Group gap="md">
                <Button
                  variant="subtle"
                  color="gray"
                  size="xs"
                  tt="uppercase"
                  fw={700}
                  leftSection={<IconShare size={14} />}
                >
                  Share
                </Button>
                <Box
                  style={{
                    width: 1,
                    height: 24,
                    backgroundColor: "var(--mantine-color-gray-3)",
                  }}
                />
                <div>
                  <Text
                    size="xs"
                    c="dimmed"
                    tt="uppercase"
                    fw={700}
                    style={{ letterSpacing: 1 }}
                  >
                    Booking Status
                  </Text>
                  <Group gap={4}>
                    <Box
                      w={8}
                      h={8}
                      style={{
                        borderRadius: "50%",
                        backgroundColor: "var(--mantine-color-yellow-6)",
                        animation:
                          "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                      }}
                    />
                    <Text size="sm" fw={700} c="yellow">
                      Pending Confirmation
                    </Text>
                  </Group>
                </div>
              </Group>
            </Paper>
          </Group>
        </Box>

        {/* Main Content */}
        <Box
          pt={76}
          h="100%"
          style={{
            overflow: "auto",
          }}
        >
          <Container size="xl" py="xl">
            <OrderHeader
              orderId={currentOrder.orderId}
              title="Review & Confirm Bookings"
              description="Please check your itinerary items below. Once confirmed, your Grab ride will be scheduled and tickets will be sent to your email."
              status={currentOrder.status}
            />

            <Grid gutter="xl">
              {/* Left Column - Booking Items */}
              <Grid.Col span={{ base: 12, lg: 8 }}>
                <Stack gap="lg">
                  {bookings.map((booking) => (
                    <BookingItemCard
                      key={booking.id}
                      booking={booking}
                      onEdit={handleEdit}
                      onRemove={handleRemove}
                    />
                  ))}
                </Stack>
              </Grid.Col>

              {/* Right Column - Payment Summary */}
              <Grid.Col span={{ base: 12, lg: 4 }}>
                <PaymentSummary
                  subtotal={pricing.subtotal}
                  serviceFee={pricing.serviceFee}
                  tax={pricing.tax}
                  total={pricing.total}
                  paymentMethods={paymentMethods}
                  selectedPaymentMethod={selectedPaymentMethod}
                  onPaymentMethodChange={setSelectedPaymentMethod}
                  onConfirmPayment={handleConfirmPayment}
                  isProcessing={isProcessing}
                />
              </Grid.Col>
            </Grid>
          </Container>
        </Box>

        {/* Add pulse animation */}
        <style>{`
          @keyframes pulse {
            0%, 100% {
              opacity: 1;
            }
            50% {
              opacity: 0.5;
            }
          }
        `}</style>
      </Box>
    </AppLayout>
  );
};

export default BookingPage;
