/**
 * In-App Purchase Service
 * ========================
 * Gerencia compras dentro do app para iOS (App Store) e Android (Google Play)
 * 
 * IMPORTANTE: Para funcionar em produção, você precisa:
 * 1. Configurar produtos no App Store Connect (iOS)
 * 2. Configurar produtos no Google Play Console (Android)
 * 3. Usar os mesmos Product IDs configurados abaixo
 */

import { Platform } from 'react-native';
import * as InAppPurchases from 'expo-in-app-purchases';

// Product IDs - Devem corresponder aos configurados nas lojas
export const IAP_PRODUCTS = {
  MONTHLY: Platform.select({
    ios: 'com.laf.subscription.monthly',
    android: 'com.laf.subscription.monthly',
    default: 'monthly',
  }),
  ANNUAL: Platform.select({
    ios: 'com.laf.subscription.annual',
    android: 'com.laf.subscription.annual',
    default: 'annual',
  }),
};

// SKUs para buscar produtos
export const IAP_SKUS = [IAP_PRODUCTS.MONTHLY, IAP_PRODUCTS.ANNUAL];

interface IAPProduct {
  productId: string;
  title: string;
  description: string;
  price: string;
  priceAmountMicros: number;
  priceCurrencyCode: string;
  subscriptionPeriod?: string;
}

interface IAPPurchase {
  productId: string;
  transactionId: string;
  transactionDate: number;
  transactionReceipt: string;
}

class IAPService {
  private isConnected: boolean = false;
  private products: IAPProduct[] = [];
  private purchaseListener: ((purchase: IAPPurchase) => void) | null = null;

  /**
   * Inicializa a conexão com a loja
   */
  async initialize(): Promise<boolean> {
    try {
      if (Platform.OS === 'web') {
        console.log('IAP not available on web');
        return false;
      }

      // Conectar à loja
      await InAppPurchases.connectAsync();
      this.isConnected = true;
      console.log('✅ IAP connected successfully');

      // Configurar listener de compras
      InAppPurchases.setPurchaseListener(({ responseCode, results, errorCode }) => {
        if (responseCode === InAppPurchases.IAPResponseCode.OK) {
          results?.forEach((purchase) => {
            if (!purchase.acknowledged) {
              console.log('🛒 Purchase received:', purchase.productId);
              
              // Finalizar a transação
              InAppPurchases.finishTransactionAsync(purchase, true);
              
              // Notificar o listener
              if (this.purchaseListener) {
                this.purchaseListener({
                  productId: purchase.productId,
                  transactionId: purchase.orderId || purchase.transactionId || '',
                  transactionDate: purchase.purchaseTime || Date.now(),
                  transactionReceipt: purchase.transactionReceipt || '',
                });
              }
            }
          });
        } else if (responseCode === InAppPurchases.IAPResponseCode.USER_CANCELED) {
          console.log('❌ User canceled the purchase');
        } else {
          console.error('❌ Purchase error:', errorCode);
        }
      });

      return true;
    } catch (error) {
      console.error('❌ Failed to initialize IAP:', error);
      return false;
    }
  }

  /**
   * Busca os produtos disponíveis na loja
   */
  async getProducts(): Promise<IAPProduct[]> {
    try {
      if (!this.isConnected) {
        await this.initialize();
      }

      const { responseCode, results } = await InAppPurchases.getProductsAsync(IAP_SKUS);

      if (responseCode === InAppPurchases.IAPResponseCode.OK && results) {
        this.products = results.map((product) => ({
          productId: product.productId,
          title: product.title,
          description: product.description,
          price: product.price,
          priceAmountMicros: product.priceAmountMicros || 0,
          priceCurrencyCode: product.priceCurrencyCode || 'BRL',
          subscriptionPeriod: product.subscriptionPeriod,
        }));
        console.log('✅ Products loaded:', this.products.length);
        return this.products;
      }

      return [];
    } catch (error) {
      console.error('❌ Failed to get products:', error);
      return [];
    }
  }

  /**
   * Inicia uma compra
   */
  async purchaseProduct(productId: string): Promise<boolean> {
    try {
      if (!this.isConnected) {
        await this.initialize();
      }

      console.log('🛒 Starting purchase for:', productId);
      await InAppPurchases.purchaseItemAsync(productId);
      return true;
    } catch (error) {
      console.error('❌ Purchase failed:', error);
      return false;
    }
  }

  /**
   * Verifica se o usuário tem uma assinatura ativa
   */
  async checkActiveSubscription(): Promise<boolean> {
    try {
      if (!this.isConnected) {
        await this.initialize();
      }

      const { responseCode, results } = await InAppPurchases.getPurchaseHistoryAsync();

      if (responseCode === InAppPurchases.IAPResponseCode.OK && results) {
        // Verificar se há alguma assinatura ativa
        const activeSubscription = results.find((purchase) => {
          // Para assinaturas, verificar se não expirou
          // Nota: A verificação completa deve ser feita no servidor
          return IAP_SKUS.includes(purchase.productId);
        });

        return !!activeSubscription;
      }

      return false;
    } catch (error) {
      console.error('❌ Failed to check subscription:', error);
      return false;
    }
  }

  /**
   * Restaura compras anteriores
   */
  async restorePurchases(): Promise<IAPPurchase[]> {
    try {
      if (!this.isConnected) {
        await this.initialize();
      }

      const { responseCode, results } = await InAppPurchases.getPurchaseHistoryAsync();

      if (responseCode === InAppPurchases.IAPResponseCode.OK && results) {
        console.log('✅ Restored purchases:', results.length);
        return results.map((purchase) => ({
          productId: purchase.productId,
          transactionId: purchase.orderId || purchase.transactionId || '',
          transactionDate: purchase.purchaseTime || Date.now(),
          transactionReceipt: purchase.transactionReceipt || '',
        }));
      }

      return [];
    } catch (error) {
      console.error('❌ Failed to restore purchases:', error);
      return [];
    }
  }

  /**
   * Define um listener para novas compras
   */
  onPurchase(callback: (purchase: IAPPurchase) => void) {
    this.purchaseListener = callback;
  }

  /**
   * Desconecta da loja
   */
  async disconnect(): Promise<void> {
    try {
      if (this.isConnected) {
        await InAppPurchases.disconnectAsync();
        this.isConnected = false;
        console.log('✅ IAP disconnected');
      }
    } catch (error) {
      console.error('❌ Failed to disconnect IAP:', error);
    }
  }

  /**
   * Verifica se IAP está disponível na plataforma atual
   */
  isAvailable(): boolean {
    return Platform.OS !== 'web';
  }

  /**
   * Retorna o produto pelo tipo de plano
   */
  getProductByPlan(planType: 'monthly' | 'annual'): IAPProduct | undefined {
    const productId = planType === 'monthly' ? IAP_PRODUCTS.MONTHLY : IAP_PRODUCTS.ANNUAL;
    return this.products.find((p) => p.productId === productId);
  }
}

// Singleton instance
export const iapService = new IAPService();
export default iapService;
