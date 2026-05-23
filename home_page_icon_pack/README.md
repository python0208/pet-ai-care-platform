# 宠护星球首页图标资源包

本资源包根据首页原型图中使用到的 UI 图标整理，适合前端开发直接放入：

```text
frontend/src/static/icons/
```

## 文件结构

```text
svg/       SVG 矢量图标，推荐开发优先使用
png/       256x256 透明 PNG 图标
manifest.json 图标清单与用途说明
```

## 图标清单

- search：顶部搜索
- bell：顶部通知铃铛
- camera：宠物头像拍照/更换头像
- deworm_bug：驱虫提醒 / 驱虫记录
- vaccine_syringe：疫苗提醒
- ai_robot：AI咨询机器人
- vaccine_record：疫苗记录
- weight_chart：体重曲线
- pet_profile：宠物档案
- location_hospital：附近医院
- shop_bag：商城 / 精选商城
- cart：加入购物车
- home：底部导航首页
- file_paw：底部导航档案
- service_heart：底部导航服务
- profile_smile：底部导航我的
- paw：装饰爪印
- chevron_right：右箭头 / 更多
- logo_star_planet：品牌星球装饰

## 使用建议

1. 小程序 / uni-app 中建议优先使用 PNG，兼容更稳。
2. H5 或 App 可优先使用 SVG，缩放更清晰。
3. 图标命名已尽量语义化，方便后续维护。
4. 商品图片、宠物头像不属于 UI 图标，因此没有放入本包。
5. 如果后续首页布局继续变化，可以继续新增或删减对应图标。

PNG conversion: success
