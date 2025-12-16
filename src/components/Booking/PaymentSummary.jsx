import React from "react";
import { Paper, Stack, Text, Group, Divider, Button, Box } from "@mantine/core";
import { IconReceipt, IconArrowRight, IconLock } from "@tabler/icons-react";
import PaymentMethodSelector from "./PaymentMethodSelector";

/**
 * Payment summary component
 * Displays pricing breakdown and payment confirmation
 */
const PaymentSummary = ({
  subtotal,
  serviceFee,
  tax,
  total,
  paymentMethods,
  selectedPaymentMethod,
  onPaymentMethodChange,
  onConfirmPayment,
  isProcessing = false,
}) => {
  const formatVND = (amount) => {
    return amount.toLocaleString("vi-VN") + "₫";
  };

  return (
    <Paper
      p="xl"
      radius="xl"
      withBorder
      shadow="lg"
      style={{
        position: "sticky",
        top: 24,
      }}
    >
      <Stack gap="lg">
        {/* Header */}
        <Group gap="xs">
          <IconReceipt size={20} color="var(--mantine-color-blue-6)" />
          <Text size="lg" fw={700}>
            Payment Summary
          </Text>
        </Group>

        {/* Price Breakdown */}
        <Stack gap="sm">
          <Group justify="space-between">
            <Text size="sm" c="dimmed">
              Subtotal
            </Text>
            <Text size="sm" fw={500}>
              {formatVND(subtotal)}
            </Text>
          </Group>

          <Group justify="space-between">
            <Text size="sm" c="dimmed">
              Service Fee
            </Text>
            <Text size="sm" fw={500}>
              {formatVND(serviceFee)}
            </Text>
          </Group>

          <Group justify="space-between">
            <Text size="sm" c="dimmed">
              Tax (8%)
            </Text>
            <Text size="sm" fw={500}>
              {formatVND(tax)}
            </Text>
          </Group>

          <Divider my="xs" />

          <Group justify="space-between" align="flex-end">
            <Text size="lg" fw={700}>
              Total
            </Text>
            <div style={{ textAlign: "right" }}>
              <Text size="xl" fw={700} c="blue" style={{ lineHeight: 1 }}>
                {formatVND(total)}
              </Text>
              <Text size="xs" c="dimmed" tt="uppercase" fw={700}>
                VND Currency
              </Text>
            </div>
          </Group>
        </Stack>

        <Divider />

        {/* Payment Method Selector */}
        <PaymentMethodSelector
          methods={paymentMethods}
          selectedMethod={selectedPaymentMethod}
          onSelect={onPaymentMethodChange}
          onAddNew={() => console.log("Add new card")}
        />

        {/* Confirm Button */}
        <Button
          size="lg"
          radius="lg"
          fullWidth
          onClick={onConfirmPayment}
          loading={isProcessing}
          rightSection={<IconArrowRight size={18} />}
          styles={{
            root: {
              position: "relative",
              overflow: "hidden",
              transition: "all 0.3s ease",
              "&:hover": {
                transform: "translateY(-2px)",
                boxShadow: "0 8px 16px rgba(59, 130, 246, 0.3)",
              },
              "&::before": {
                content: '""',
                position: "absolute",
                top: 0,
                left: "-100%",
                width: "100%",
                height: "100%",
                background:
                  "linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent)",
                transition: "left 0.7s ease",
              },
              "&:hover::before": {
                left: "100%",
              },
            },
          }}
        >
          Confirm & Pay Securely
        </Button>

        {/* Security Badge */}
        <Group justify="center" gap="xs">
          <IconLock size={14} color="var(--mantine-color-gray-5)" />
          <Text size="xs" c="dimmed">
            Processed with Secure 256-bit SSL Encryption
          </Text>
        </Group>
      </Stack>
    </Paper>
  );
};

export default PaymentSummary;
