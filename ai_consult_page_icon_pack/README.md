# AI 咨询首页图标资源包

本资源包用于「AI养宠助手 / AI咨询首页」原型图开发，适合放入前端静态目录。

建议放置路径：

```text
frontend/src/static/icons/ai/
```

或根据项目现有结构合并到：

```text
frontend/src/static/icons/
frontend/src/static/images/
```

## 文件结构

```text
svg/              SVG 矢量图标
png/              256x256 透明 PNG 图标
manifest.json     图标用途说明
README.md         使用说明
```

## 资源清单

- ai_robot：AI 咨询入口与通用机器人图标
- robot_header：顶部 Hero 区机器人插画图标
- shield_notice：免责声明提示条盾牌图标
- pet_selected_check：当前宠物选中状态勾选图标
- add_pet_plus：添加宠物入口图标
- quick_health：快捷问题分类：健康咨询
- quick_daily_care：快捷问题分类：日常养护
- quick_archive：快捷问题分类：档案记录
- input_bot：新咨询输入入口左侧机器人图标
- history_vaccine：历史咨询：疫苗记录图标
- history_deworm：历史咨询：驱虫记录图标
- history_question：历史咨询：普通问题图标
- history_skin：历史咨询：皮肤/瘙痒问题图标
- tag_health：类型标签：健康咨询
- tag_draft：类型标签：记录草稿
- chevron_right：右箭头 / 进入详情
- tab_home：底部导航：首页
- tab_archive：底部导航：档案
- tab_ai_active：底部导航：AI咨询 active
- tab_service：底部导航：服务
- tab_mine：底部导航：我的
- paw_accent：装饰爪印
- pet_avatar_placeholder：宠物头像占位图
- view_all：查看全部 / 更多入口

## 使用建议

1. 小程序端优先使用 PNG，兼容更稳。
2. H5/App 可优先使用 SVG，缩放更清晰。
3. 用户真实宠物头像不属于本静态资源包，仍走上传接口。
4. 如果图标和已有 `home_page_icon_pack/` 或 `archive_page_assets_pack/` 重复，可以优先保留现有命名，避免重复导入。
5. 建议 Codex 将本包复制到：
   ```text
   frontend/src/static/icons/ai/
   ```

PNG conversion: success
