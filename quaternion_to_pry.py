
import math

def quaternion_to_rpy(qx, qy, qz, qw):
    """
    Convert quaternion (qx, qy, qz, qw) to roll, pitch, and yaw (RPY).

    Args:
        qx (float): X component of the quaternion.
        qy (float): Y component of the quaternion.
        qz (float): Z component of the quaternion.
        qw (float): W component of the quaternion.

    Returns:
        tuple: (roll, pitch, yaw) in radians.
    """
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2 * (qw * qy - qz * qx)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)

    # Yaw (z-axis rotation)
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw

def rpy_to_quaternion(roll, pitch, yaw):
    """
    Convert roll, pitch, and yaw (RPY) to a quaternion (qx, qy, qz, qw).

    Args:
        roll (float): Roll angle in radians.
        pitch (float): Pitch angle in radians.
        yaw (float): Yaw angle in radians.

    Returns:
        tuple: (qx, qy, qz, qw) components of the quaternion.
    """
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy

    return qx, qy, qz, qw
# Example usage
if __name__ == "__main__":
    qw, qx, qy, qz = 1.0, 0.0, 0.0, 0.0  # Example quaternion
    qw, qx, qy, qz = 0.7, 0.0, 0.7, 0.0  # Example quaternion
    roll, pitch, yaw = quaternion_to_rpy(qx, qy, qz, qw)

    print(f"Roll: {math.degrees(roll):.2f}°")
    print(f"Pitch: {math.degrees(pitch):.2f}°")
    print(f"Yaw: {math.degrees(yaw):.2f}°")

    r, p, y = 0, 90, 0
    qw, qx, qy, qz = rpy_to_quaternion(r, p, y)
    print(f"qw: {qw:.2f} qx: {qx:.2f} qy: {qy:.2f} qz: {qz:.2f}")
