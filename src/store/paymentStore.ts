// src/store/paymentStore.ts
import { defineStore } from 'pinia';
import axios from 'axios';

interface PaymentState {
  isPaid: boolean;
  expireAt: string | null;
  loading: boolean;
}

export const usePaymentStore = defineStore('payment', {
  state: (): PaymentState => ({
    isPaid: false,
    expireAt: null,
    loading: false
  }),
  actions: {
    async checkPaymentStatus() {
      this.loading = true;
      try {
        const response = await axios.get('/api/check-payment');
        this.isPaid = response.data.is_paid;
        this.expireAt = response.data.expire_at;
      } catch (error) {
        console.error('支付状态检查失败:', error);
        this.isPaid = false;
      } finally {
        this.loading = false;
      }
    },
    
    setPaymentStatus(status: boolean, expireAt: string | null = null) {
      this.isPaid = status;
      this.expireAt = expireAt;
    }
  }
});