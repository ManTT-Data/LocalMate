import React, { useState } from "react";
import PropTypes from "prop-types";
import { Modal, TextInput, Stack, Button, Group } from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { notifications } from "@mantine/notifications";
import { updateItineraryAPI } from "../../apis/itineraryService";
import useItineraryStore from "../../stores/useItineraryStore";

const EditItineraryModal = ({ opened, onClose, itinerary }) => {
  const [title, setTitle] = useState(itinerary?.title || "");
  const [startDate, setStartDate] = useState(
    itinerary?.start_date ? new Date(itinerary.start_date) : new Date()
  );
  const [endDate, setEndDate] = useState(
    itinerary?.end_date ? new Date(itinerary.end_date) : new Date()
  );
  const [loading, setLoading] = useState(false);

  const { fetchItineraries } = useItineraryStore();

  const handleSave = async () => {
    // Validation
    if (!title.trim()) {
      notifications.show({
        title: "Error",
        message: "Title is required",
        color: "red",
      });
      return;
    }

    if (endDate < startDate) {
      notifications.show({
        title: "Error",
        message: "End date must be after start date",
        color: "red",
      });
      return;
    }

    try {
      setLoading(true);

      const totalDays =
        Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;

      await updateItineraryAPI(itinerary.id, {
        title,
        start_date: startDate.toISOString().split("T")[0],
        end_date: endDate.toISOString().split("T")[0],
        total_days: totalDays,
      });

      // Refresh itineraries
      await fetchItineraries();

      notifications.show({
        title: "Success",
        message: "Itinerary updated successfully",
        color: "green",
      });

      onClose();
    } catch (error) {
      console.error("Error updating itinerary:", error);
      notifications.show({
        title: "Error",
        message: "Failed to update itinerary",
        color: "red",
      });
    } finally {
      setLoading(false);
    }
  };

  // Update state when itinerary prop changes
  React.useEffect(() => {
    if (itinerary) {
      setTitle(itinerary.title || "");
      setStartDate(
        itinerary.start_date ? new Date(itinerary.start_date) : new Date()
      );
      setEndDate(
        itinerary.end_date ? new Date(itinerary.end_date) : new Date()
      );
    }
  }, [itinerary]);

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title="Edit Itinerary"
      size="md"
      centered
    >
      <Stack>
        <TextInput
          label="Title"
          placeholder="My Trip to Da Nang"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />

        <DateInput
          label="Start Date"
          placeholder="Select start date"
          value={startDate}
          onChange={setStartDate}
          required
        />

        <DateInput
          label="End Date"
          placeholder="Select end date"
          value={endDate}
          onChange={setEndDate}
          minDate={startDate}
          required
        />

        <Group justify="flex-end" mt="md">
          <Button variant="subtle" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleSave} loading={loading}>
            Save Changes
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
};

EditItineraryModal.propTypes = {
  opened: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  itinerary: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string,
    start_date: PropTypes.string,
    end_date: PropTypes.string,
  }),
};

export default EditItineraryModal;
