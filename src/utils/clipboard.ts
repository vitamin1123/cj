// src/utils/clipboard.ts
export const copyTextToClipboard = (text: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    if (navigator.clipboard) {
      // 现代浏览器使用 Clipboard API
      navigator.clipboard.writeText(text)
        .then(() => resolve())
        .catch(err => reject(err));
    } else {
      // 兼容旧版浏览器的实现
      try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.top = '0';
        textArea.style.left = '0';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        const success = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        success ? resolve() : reject(new Error('复制失败'));
      } catch (err) {
        reject(err);
      }
    }
  });
};