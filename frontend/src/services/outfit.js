/**
 * 是否使用 Mock 数据
 */
const USE_MOCK = true

/**
 * AI 搭配生成 —— 统一入口
 * 当前使用 Mock，切换 USE_MOCK 即可对接后端
 * @param {Object} params - { scene, weather, wardrobeIds }
 * @returns {Promise<Object>} { outfits: [...] }
 */
export async function generateOutfit(params) {
  if (USE_MOCK) {
    return generateOutfitMock(params)
  }
  return generateOutfitMock(params)
}

// ==================== Mock 实现 ====================

async function generateOutfitMock(params) {
  const { scene = 'casual', weather } = params

  return new Promise((resolve) => {
    const delay = 2500 + Math.random() * 1000
    setTimeout(() => {
      resolve({
        outfits: generateMockOutfits(scene, weather)
      })
    }, delay)
  })
}

function generateMockOutfits(scene, weather) {
  const sceneMap = {
    commute: { name: '通勤', outfits: commuteOutfits },
    date: { name: '约会', outfits: dateOutfits },
    casual: { name: '休闲', outfits: casualOutfits },
    sports: { name: '运动', outfits: sportsOutfits },
    party: { name: '派对', outfits: partyOutfits }
  }

  const config = sceneMap[scene] || sceneMap.casual
  const baseOutfits = config.outfits

  return baseOutfits.map((o, i) => ({
    outfitId: `AI-${Date.now().toString(36).toUpperCase()}-${i}`,
    scene: config.name,
    matchRate: 90 + Math.floor(Math.random() * 9),
    top: o.top,
    bottom: o.bottom,
    shoes: o.shoes,
    accessory: o.accessory,
    reason: o.reason,
    weatherNote: weather ? `考虑今日${weather.temp}°C天气，${weather.desc}` : '基于您的风格偏好推荐'
  }))
}

const commuteOutfits = [
  {
    top: { id: 101, name: '白色修身衬衫', image: 'https://picsum.photos/200?random=21', category: 'top' },
    bottom: { id: 102, name: '深蓝色西装裤', image: 'https://picsum.photos/200?random=22', category: 'bottom' },
    shoes: { id: 103, name: '黑色尖头高跟鞋', image: 'https://picsum.photos/200?random=23', category: 'shoes' },
    accessory: { id: 104, name: '简约通勤托特包', image: 'https://picsum.photos/200?random=24', category: 'bag' },
    reason: '经典蓝白配色干练专业，修身剪裁凸显腰线，阔腿裤修饰腿型，适合全天候办公环境。'
  },
  {
    top: { id: 201, name: '米色真丝衬衫', image: 'https://picsum.photos/200?random=25', category: 'top' },
    bottom: { id: 202, name: '灰色烟管裤', image: 'https://picsum.photos/200?random=26', category: 'bottom' },
    shoes: { id: 203, name: '裸色低跟鞋', image: 'https://picsum.photos/200?random=27', category: 'shoes' },
    accessory: { id: 204, name: '珍珠耳钉', image: 'https://picsum.photos/200?random=28', category: 'accessory' },
    reason: '柔和大地色系温婉知性，真丝材质提升质感，烟管裤平衡正式感与舒适度，见客户首选。'
  },
  {
    top: { id: 301, name: '黑色高领毛衣', image: 'https://picsum.photos/200?random=29', category: 'top' },
    bottom: { id: 302, name: '直筒牛仔裤', image: 'https://picsum.photos/200?random=30', category: 'bottom' },
    shoes: { id: 303, name: '白色运动鞋', image: 'https://picsum.photos/200?random=31', category: 'shoes' },
    accessory: { id: 304, name: '黑色手提包', image: 'https://picsum.photos/200?random=32', category: 'bag' },
    reason: '这套搭配非常适合今天的天气，复古且保暖。黑色高领显瘦，直筒牛仔裤修饰腿型，白色运动鞋点亮全身。'
  }
]

const dateOutfits = [
  {
    top: { id: 401, name: '法式碎花衬衫', image: 'https://picsum.photos/200?random=33', category: 'top' },
    bottom: { id: 402, name: 'A字高腰短裙', image: 'https://picsum.photos/200?random=34', category: 'bottom' },
    shoes: { id: 403, name: '细带凉鞋', image: 'https://picsum.photos/200?random=35', category: 'shoes' },
    accessory: { id: 404, name: '金色锁骨链', image: 'https://picsum.photos/200?random=36', category: 'accessory' },
    reason: '温柔碎花搭配高腰A字裙拉长比例，金色饰品增添精致感，甜美中带着小性感。'
  },
  {
    top: { id: 501, name: '一字肩针织衫', image: 'https://picsum.photos/200?random=37', category: 'top' },
    bottom: { id: 502, name: '白色阔腿裤', image: 'https://picsum.photos/200?random=38', category: 'bottom' },
    shoes: { id: 503, name: '尖头穆勒鞋', image: 'https://picsum.photos/200?random=39', category: 'shoes' },
    accessory: { id: 504, name: '珍珠手链', image: 'https://picsum.photos/200?random=40', category: 'accessory' },
    reason: '一字肩展现迷人锁骨，上紧下松的廓形优雅大方，白色裤装让整体轻盈明亮。'
  },
  {
    top: { id: 601, name: '红色丝绒吊带', image: 'https://picsum.photos/200?random=41', category: 'top' },
    bottom: { id: 602, name: '黑色喇叭裤', image: 'https://picsum.photos/200?random=42', category: 'bottom' },
    shoes: { id: 603, name: '黑色漆皮高跟', image: 'https://picsum.photos/200?random=43', category: 'shoes' },
    accessory: { id: 604, name: '银色流苏耳环', image: 'https://picsum.photos/200?random=44', category: 'accessory' },
    reason: '红黑经典配色热情又高级，丝绒材质自带复古滤镜，喇叭裤复古回潮，约会氛围感拉满。'
  }
]

const casualOutfits = [
  {
    top: { id: 701, name: '灰色宽松卫衣', image: 'https://picsum.photos/200?random=45', category: 'top' },
    bottom: { id: 702, name: '卡其色休闲裤', image: 'https://picsum.photos/200?random=46', category: 'bottom' },
    shoes: { id: 703, name: '复古跑鞋', image: 'https://picsum.photos/200?random=47', category: 'shoes' },
    accessory: { id: 704, name: '帆布托特包', image: 'https://picsum.photos/200?random=48', category: 'bag' },
    reason: '舒适慵懒的周末标配，卫衣+休闲裤自在随性，复古跑鞋增添街头感，逛街一整天不累。'
  },
  {
    top: { id: 801, name: '条纹短袖T恤', image: 'https://picsum.photos/200?random=49', category: 'top' },
    bottom: { id: 802, name: '牛仔短裤', image: 'https://picsum.photos/200?random=50', category: 'bottom' },
    shoes: { id: 803, name: '白色帆布鞋', image: 'https://picsum.photos/200?random=51', category: 'shoes' },
    accessory: { id: 804, name: '鸭舌帽', image: 'https://picsum.photos/200?random=52', category: 'accessory' },
    reason: '经典条纹+牛仔的组合永远不过时，帆布鞋减龄满分，帽子既能遮阳又能提升造型感。'
  },
  {
    top: { id: 901, name: '白色基础款T恤', image: 'https://picsum.photos/200?random=53', category: 'top' },
    bottom: { id: 902, name: '浅色直筒牛仔裤', image: 'https://picsum.photos/200?random=54', category: 'bottom' },
    shoes: { id: 903, name: '厚底德训鞋', image: 'https://picsum.photos/200?random=55', category: 'shoes' },
    accessory: { id: 904, name: '黑色斜挎包', image: 'https://picsum.photos/200?random=56', category: 'bag' },
    reason: '极简风白T+直筒牛仔清爽利落，德训鞋脚感舒适，斜挎包解放双手，日常出门首选。'
  }
]

const sportsOutfits = [
  {
    top: { id: 1001, name: '速干运动背心', image: 'https://picsum.photos/200?random=57', category: 'top' },
    bottom: { id: 1002, name: '高腰瑜伽裤', image: 'https://picsum.photos/200?random=58', category: 'bottom' },
    shoes: { id: 1003, name: '缓震跑鞋', image: 'https://picsum.photos/200?random=59', category: 'shoes' },
    accessory: { id: 1004, name: '运动发带', image: 'https://picsum.photos/200?random=60', category: 'accessory' },
    reason: '专业运动装备保证运动表现，速干面料透气排汗，高腰设计提供支撑，跑鞋缓震保护膝盖。'
  },
  {
    top: { id: 1101, name: '拉链运动夹克', image: 'https://picsum.photos/200?random=61', category: 'top' },
    bottom: { id: 1102, name: '宽松运动短裤', image: 'https://picsum.photos/200?random=62', category: 'bottom' },
    shoes: { id: 1103, name: '综训鞋', image: 'https://picsum.photos/200?random=63', category: 'shoes' },
    accessory: { id: 1104, name: '运动水壶', image: 'https://picsum.photos/200?random=64', category: 'accessory' },
    reason: '层次感运动穿搭，夹克热身时穿，热身后脱掉，综训鞋适应多种运动场景。'
  },
  {
    top: { id: 1201, name: '拼接色运动T恤', image: 'https://picsum.photos/200?random=65', category: 'top' },
    bottom: { id: 1202, name: '紧身运动长裤', image: 'https://picsum.photos/200?random=66', category: 'bottom' },
    shoes: { id: 1203, name: '轻量跑鞋', image: 'https://picsum.photos/200?random=67', category: 'shoes' },
    accessory: { id: 1204, name: '运动手环', image: 'https://picsum.photos/200?random=68', category: 'accessory' },
    reason: '亮色拼接提升运动心情，紧身裤减少风阻，轻量跑鞋适合长距离训练，手环记录运动数据。'
  }
]

const partyOutfits = [
  {
    top: { id: 1301, name: '亮片吊带衫', image: 'https://picsum.photos/200?random=69', category: 'top' },
    bottom: { id: 1302, name: '高腰皮裙', image: 'https://picsum.photos/200?random=70', category: 'bottom' },
    shoes: { id: 1303, name: '铆钉高跟靴', image: 'https://picsum.photos/200?random=71', category: 'shoes' },
    accessory: { id: 1304, name: '水钻choker', image: 'https://picsum.photos/200?random=72', category: 'accessory' },
    reason: '全场焦点穿搭！亮片在灯光下闪耀吸睛，皮质元素增加酷感，铆钉靴彰显个性态度。'
  },
  {
    top: { id: 1401, name: '丝绒深V连体衣', image: 'https://picsum.photos/200?random=73', category: 'top' },
    bottom: { id: 1402, name: '亮面阔腿裤', image: 'https://picsum.photos/200?random=74', category: 'bottom' },
    shoes: { id: 1403, name: '细跟一字带', image: 'https://picsum.photos/200?random=75', category: 'shoes' },
    accessory: { id: 1404, name: '水晶手拿包', image: 'https://picsum.photos/200?random=76', category: 'bag' },
    reason: '丝绒的高级感搭配亮面裤装的流动光泽，行走间步步生辉，手拿包精致不累赘。'
  },
  {
    top: { id: 1501, name: '斜肩不对称上衣', image: 'https://picsum.photos/200?random=77', category: 'top' },
    bottom: { id: 1502, name: '流苏半身裙', image: 'https://picsum.photos/200?random=78', category: 'bottom' },
    shoes: { id: 1503, name: '绑带高跟凉鞋', image: 'https://picsum.photos/200?random=79', category: 'shoes' },
    accessory: { id: 1504, name: '金属大耳环', image: 'https://picsum.photos/200?random=80', category: 'accessory' },
    reason: '不对称设计艺术感十足，流苏裙摆动间灵动飘逸，绑带鞋延伸腿部线条，派对女王就是你。'
  }
]

