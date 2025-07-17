// 分批处理工具函数
export async function processInBatches<T, R>(
  items: T[],
  batchProcessor: (batch: T[]) => R[],
  batchSize: number = 50,
  delayMs: number = 16 // ~60fps
): Promise<R[]> {
  const results: R[] = [];

  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = batchProcessor(batch);
    results.push(...batchResults);

    // ✅ 让出主线程，防止卡顿
    await new Promise(resolve => setTimeout(resolve, delayMs));
  }

  return results;
}