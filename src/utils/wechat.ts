import wx from 'weixin-js-sdk';
import apiClient from '@/plugins/axios';

// 定义微信配置对象类型
interface WechatConfig {
  appId: string;
  timestamp: string;
  nonceStr: string;
  signature: string;
}

// 定义分享选项类型
interface ShareOptions {
  title: string;
  desc: string;
  link: string;
  imgUrl: string;
  success?: () => void;
  cancel?: () => void;
}

/**
 * 获取微信签名配置
 * @param url 当前页面的完整URL（不包含#及其后面部分）
 * @returns Promise<WechatConfig>
 */
export const getWechatConfig = async (url: string): Promise<WechatConfig> => {
  try {
    const response = await apiClient.get('/api/wechat/jssdk-signature', {
      params: { url }
    });
    return response.data as WechatConfig;
  } catch (error) {
    console.error('获取微信签名失败:', error);
    throw error;
  }
};

/**
 * 初始化微信JS-SDK
 * @param url 当前页面的完整URL（不包含#及其后面部分）
 * @returns Promise<void>
 */
export const initWechatSDK = async (url: string): Promise<void> => {
  try {
    // 获取签名配置
    const config = await getWechatConfig(url);
    
    // 配置微信JS-SDK
    wx.config({
      debug: false,
      appId: config.appId,
      timestamp: parseInt(config.timestamp),
      nonceStr: config.nonceStr,
      signature: config.signature,
      jsApiList: [
        'updateAppMessageShareData',
        'updateTimelineShareData',
        'onMenuShareAppMessage',
        'onMenuShareTimeline',
        'showOptionMenu'
      ]
    });
    
    return new Promise<void>((resolve, reject) => {
      wx.ready(() => {
        console.log('微信JS-SDK初始化成功');
        resolve();
      });
      
      wx.error((err) => {
        console.error('微信JS-SDK初始化失败:', err);
        reject(err);
      });
    });
  } catch (error) {
    console.error('初始化微信JS-SDK出错:', error);
    throw error;
  }
};

/**
 * 设置微信分享信息
 * @param options 分享配置选项
 */
export const setWechatShareInfo = (options: Partial<ShareOptions>): void => {
  const defaultOptions: ShareOptions = {
    title: '默认分享标题',
    desc: '默认分享描述',
    link: window.location.href,
    imgUrl: 'http://www.tianshunchenjie.com/photo/tianshun.png',
    success: () => {},
    cancel: () => {}
  };
  
  const shareOptions: ShareOptions = { ...defaultOptions, ...options };
  
  // 自定义"分享给朋友"按钮
  wx.onMenuShareAppMessage({
    title: shareOptions.title,
    desc: shareOptions.desc,
    link: shareOptions.link,
    imgUrl: shareOptions.imgUrl,
    success: shareOptions.success || (() => {}),
    cancel: shareOptions.cancel || (() => {})
  });
  
  // 自定义"分享到朋友圈"按钮
  wx.onMenuShareTimeline({
    title: shareOptions.title,
    link: shareOptions.link,
    imgUrl: shareOptions.imgUrl,
    success: shareOptions.success || (() => {}),
    cancel: shareOptions.cancel || (() => {})
  });
  
  // 显示分享按钮
  wx.showOptionMenu();
};