import pytest
from app.models import AppointmentStatus
from app.routers.appointments import validate_transition


class TestAppointmentStateMachine:
    """订单状态机测试"""

    def test_normal_flow(self):
        """测试正常流程"""
        flow = [
            AppointmentStatus.PENDING_ACCEPT,
            AppointmentStatus.ACCEPTED,
            AppointmentStatus.TO_ATTEND,
            AppointmentStatus.IN_PROGRESS,
            AppointmentStatus.EVALUATING,
            AppointmentStatus.COMPLETED
        ]
        for i in range(len(flow) - 1):
            # 正常流程不应抛出异常
            validate_transition(flow[i], flow[i + 1])

    def test_invalid_transition(self):
        """测试非法状态转换"""
        with pytest.raises(Exception) as exc_info:
            # completed 不能回到 accepted
            validate_transition(
                AppointmentStatus.COMPLETED,
                AppointmentStatus.ACCEPTED
            )
        assert "订单状态不允许" in str(exc_info.value.detail["message"])

    def test_cancel_from_pending(self):
        """测试待接单状态可以取消"""
        # 不应抛出异常
        validate_transition(
            AppointmentStatus.PENDING_ACCEPT,
            AppointmentStatus.CANCELLED
        )

    def test_refund_flow(self):
        """测试退款流程"""
        # accepted -> refunding
        validate_transition(
            AppointmentStatus.ACCEPTED,
            AppointmentStatus.REFUNDING
        )

        # refunding -> refunded
        validate_transition(
            AppointmentStatus.REFUNDING,
            AppointmentStatus.REFUNDED
        )

    def test_cannot_skip_status(self):
        """测试不能跳过状态"""
        with pytest.raises(Exception):
            # pending_accept 不能直接到 to_attend
            validate_transition(
                AppointmentStatus.PENDING_ACCEPT,
                AppointmentStatus.TO_ATTEND
            )
