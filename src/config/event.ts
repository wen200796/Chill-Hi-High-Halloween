/**
 * 品牌名稱與活動資訊（最高優先級）。
 * 影片中所有活動文字都從這裡讀取，請只在這裡修改。
 * 注意：正式品牌名稱為「Chill Hi High」，三個英文單字之間有空格。
 */
export const BRAND = {
  name: 'Chill Hi High',
  eventName: 'Chill Hi High Halloween Toastmasters',
  /** 片尾主標的分行顯示（合起來即為正式活動名稱） */
  titleLines: {
    brand: 'Chill Hi High',
    halloween: 'Halloween',
    toastmasters: 'Toastmasters',
  },
  logo: 'assets/chill_hi_high_logo.png',
} as const;

export const EVENT = {
  date: '10/27（二）',
  time: '19:15–21:15',
  venue: '社會創新實驗中心 107 會議室',
  address: '臺北市大安區仁愛路三段 99 號',
} as const;
