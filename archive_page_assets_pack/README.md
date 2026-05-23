# 档案管理页面图片资源包

本资源包用于宠护星球项目的「档案管理」页面开发，参考原型图：

```text
docs/page/archive_page.png
```

建议放置路径：

```text
frontend/src/static/archive-icons/
```

或按项目当前资源目录合并到：

```text
frontend/src/static/icons/
frontend/src/static/images/
```

## 包含内容

```text
svg/              SVG 矢量资源，适合 H5/App 或组件直接引用
png/              256x256 透明 PNG，适合 uni-app / 小程序稳定使用
manifest.json     资源用途说明
README.md         本说明文件
```

## 资源清单

- default_pet_avatar：默认宠物头像
- archive_folder：基础信息
- vaccine_record：疫苗记录
- deworm_record：驱虫记录
- medical_record：就诊记录
- allergy_shield：过敏史
- weight_curve：体重曲线 / 体重趋势
- neutered：已绝育状态
- healthy_shield：健康中状态
- recent_clock：近期记录
- add_pet：新增宠物 / 空状态
- camera_badge：头像更换相机图标
- chevron_right：右箭头
- calendar：日期图标
- empty_pet：无宠物档案空状态插画
- tab_home：底部导航首页
- tab_archive_active：底部导航档案 active
- tab_ai：底部导航 AI咨询
- tab_service：底部导航服务
- tab_mine：底部导航我的
- paw_accent：装饰爪印

## 使用建议

1. 小程序端优先使用 PNG，兼容性更稳。
2. H5/App 可优先使用 SVG，缩放更清晰。
3. `default_pet_avatar.svg` 建议复制到：
   ```text
   frontend/src/static/images/default-pet-avatar.svg
   ```
4. 其他模块图标可放到：
   ```text
   frontend/src/static/icons/archive/
   ```
5. 用户上传的真实宠物头像不属于静态资源，不应该提交 Git。
6. `media/` 目录必须继续保持在 `.gitignore` 中。

PNG conversion: success
