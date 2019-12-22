# Device Registry Service

## Usage

All response will have the form

```json
{
    "data": "Mixed type holding the content of the response",
    "message": "description of what happened"
}
```

### List all devices

**Definition**

`GET /devices`

**Response**

- `200 OK` on success

```json
[
    {
        "identifier":  "floor-lamp",
        "name": "Floor Lamp",
        "device_type": "switch",
        "controller_gateway": "192.168.0.2"
    },
    {
        "identifier":  "samsung-tv",
        "name": "Samsung TV",
        "device_type": "tv",
        "controller_gateway": "192.168.0.9"
    }
]
```

### Registering new device

**Definition**

`POST /devices`

**Arguments**

- `"identifier": string` a globally unique identifier for this device
- `"name": string` a friendly name for this device
- `"device_type":string` the type of the device
- `"controller_gateway":string` the IP address of the device

**Response**

- `200 OK` on success

```json

```