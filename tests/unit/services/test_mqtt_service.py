import pytest
from unittest.mock import Mock, patch, call
from src.services.mqtt_service import MQTTService


@pytest.fixture
def mock_devices():
    """Mock a list of devices with necessary methods."""
    mock_device_1 = Mock()
    mock_device_1.device_class = "garage"
    mock_device_1.device_id = 1
    mock_device_1.get_topic.side_effect = lambda t: f"{t}/garage/1"
    mock_device_1.get_status.return_value = '{"status": "ok"}'
    mock_device_1.handle_command = Mock()

    mock_device_2 = Mock()
    mock_device_2.device_class = "motion"
    mock_device_2.device_id = 2
    mock_device_2.get_topic.side_effect = lambda t: f"{t}/motion/2"
    mock_device_2.get_status.return_value = '{"status": "active"}'
    mock_device_2.handle_command = Mock()

    return [mock_device_1, mock_device_2]


@pytest.fixture
def mock_mqtt_client():
    """Mock the paho MQTT client."""
    with patch("paho.mqtt.client.Client", autospec=True) as mock_client_class:
        yield mock_client_class.return_value


@pytest.fixture
def mqtt_service(mock_devices, mock_mqtt_client):
    """Initialize MQTTService with mocks."""
    service = MQTTService(
        host="localhost",
        port=1883,
        username="user",
        password="pass",
        devices=mock_devices,
        interval=1,
    )
    return service


def test_mqtt_service_on_connect(mqtt_service, mock_mqtt_client, mock_devices):
    """Test the `on_connect` method."""
    mqtt_service.on_connect(mock_mqtt_client, None, None, 0)

    # Ensure subscription to device topics
    expected_calls = [call(device.get_topic("command")) for device in mock_devices]
    mock_mqtt_client.subscribe.assert_has_calls(expected_calls)

    # Check logging and connection handling
    mock_mqtt_client.subscribe.assert_called()
    assert mock_mqtt_client.subscribe.call_count == len(mock_devices)


def test_mqtt_service_on_message(mqtt_service, mock_devices):
    """Test the `on_message` method with valid and invalid topics."""
    valid_message = Mock()
    valid_message.topic = "command/garage/1"
    valid_message.payload = b'{"action": "open"}'

    invalid_message = Mock()
    invalid_message.topic = "command/unknown/1"

    # Handle valid message
    mqtt_service.on_message(None, None, valid_message)
    mock_devices[0].handle_command.assert_called_once_with('{"action": "open"}')

    # Handle invalid message
    mqtt_service.on_message(None, None, invalid_message)
    mock_devices[0].handle_command.assert_called_once()  # No additional call
    mock_devices[1].handle_command.assert_not_called()


def test_mqtt_service_publish(mqtt_service, mock_mqtt_client):
    """Test the `publish` method."""
    mqtt_service.publish("test/topic", '{"key": "value"}', retain=True)

    mock_mqtt_client.publish.assert_called_once_with("test/topic", '{"key": "value"}', retain=True, qos=2)


def test_mqtt_service_publish_status(mqtt_service, mock_mqtt_client, mock_devices):
    """Test the `publish_status` method."""
    mqtt_service.publish_status()

    for device in mock_devices:
        topic = device.get_topic("status")
        payload = device.get_status()
        mock_mqtt_client.publish.assert_any_call(topic, payload, retain=True, qos=2)


def test_mqtt_service_handle_device_state_change(mqtt_service, mock_mqtt_client):
    """Test the `handle_device_state_change` method."""
    mqtt_service.handle_device_state_change("garage", 1, '{"state": "open"}')

    mock_mqtt_client.publish.assert_called_once_with(
        "state/garage/1", '{"state": "open"}', retain=False, qos=2
    )


def test_mqtt_service_start_and_stop(mqtt_service, mock_mqtt_client):
    """Test the `start` and `stop` methods."""
    with patch("threading.Thread.start") as mock_thread_start:
        mqtt_service.start()
        mock_mqtt_client.connect.assert_called_once_with("localhost", 1883)
        mock_mqtt_client.loop_start.assert_called_once()
        mock_thread_start.assert_called_once()

    with patch("threading.Thread.join") as mock_thread_join:
        mqtt_service.stop()
        mqtt_service.stop_event.set()
        mock_mqtt_client.loop_stop.assert_called_once()
        mock_mqtt_client.disconnect.assert_called_once()
        mock_thread_join.assert_called_once()


def test_mqtt_service_publish_status_periodically(mqtt_service):
    """Test the `publish_status_periodically` method."""
    with patch.object(mqtt_service, "publish_status", wraps=mqtt_service.publish_status) as mock_publish_status:
        mqtt_service.stop_event.set()  # Stop immediately
        mqtt_service.publish_status_periodically()
        mock_publish_status.assert_not_called()
