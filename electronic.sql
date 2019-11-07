/*
 Navicat Premium Data Transfer

 Source Server         : FundingBasedOnBlockchain
 Source Server Type    : MySQL
 Source Server Version : 50725
 Source Host           : localhost:3306
 Source Schema         : electronic

 Target Server Type    : MySQL
 Target Server Version : 50725
 File Encoding         : 65001

 Date: 07/11/2019 09:18:41
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alembic_version
-- ----------------------------
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version`  (
  `version_num` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`version_num`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of alembic_version
-- ----------------------------
INSERT INTO `alembic_version` VALUES ('7b2d8d464098');

-- ----------------------------
-- Table structure for certs
-- ----------------------------
DROP TABLE IF EXISTS `certs`;
CREATE TABLE `certs`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `resource_id` int(11) DEFAULT NULL,
  `transfer_id` int(11) DEFAULT NULL,
  `payer_id` int(11) DEFAULT NULL,
  `value` int(11) DEFAULT NULL,
  `timestamp_pay` datetime(0) DEFAULT NULL,
  `timestamp_trans` datetime(0) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `resource_id`(`resource_id`) USING BTREE,
  INDEX `payer_id`(`payer_id`) USING BTREE,
  INDEX `transfer_id`(`transfer_id`) USING BTREE,
  INDEX `ix_certs_timestamp_pay`(`timestamp_pay`) USING BTREE,
  CONSTRAINT `certs_ibfk_2` FOREIGN KEY (`resource_id`) REFERENCES `resource` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `certs_ibfk_4` FOREIGN KEY (`payer_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `certs_ibfk_5` FOREIGN KEY (`transfer_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 17 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of certs
-- ----------------------------
INSERT INTO `certs` VALUES (11, 3, NULL, 5, 1, '2019-11-06 14:34:34', NULL);
INSERT INTO `certs` VALUES (12, 3, 7, 8, 1, '2019-11-06 23:23:30', '2019-11-06 23:23:58');
INSERT INTO `certs` VALUES (13, 3, NULL, 7, 1, '2019-11-06 23:23:58', NULL);
INSERT INTO `certs` VALUES (14, 3, 6, 8, 1, '2019-11-06 23:24:11', '2019-11-06 23:24:22');
INSERT INTO `certs` VALUES (15, 3, NULL, 6, 1, '2019-11-06 23:24:22', NULL);
INSERT INTO `certs` VALUES (16, 3, NULL, 4, 1, '2019-11-06 23:25:36', NULL);

-- ----------------------------
-- Table structure for resource
-- ----------------------------
DROP TABLE IF EXISTS `resource`;
CREATE TABLE `resource`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `body` varchar(140) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `timestamp` datetime(0) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `price` int(11) DEFAULT NULL,
  `title` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `filename` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `updatetime` datetime(0) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_resource_timestamp`(`timestamp`) USING BTREE,
  INDEX `user_id`(`user_id`) USING BTREE,
  CONSTRAINT `resource_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of resource
-- ----------------------------
INSERT INTO `resource` VALUES (3, '这是kimroniny的第一份数据', '2019-11-04 01:29:01', 3, 1, 'kimroniny`s first data', 'k_1.txt', '2019-11-06 15:13:21');
INSERT INTO `resource` VALUES (4, '这是k的第二条数据', '2019-11-04 05:48:53', 3, 20, 'kimroniny`s second data', 'k_2.txt', '2019-11-06 15:13:57');
INSERT INTO `resource` VALUES (5, '这是k的第三条数据', '2019-11-04 05:49:42', 3, 20, 'kimroniny`s third data', 'k_3.txt', '2019-11-06 15:14:17');
INSERT INTO `resource` VALUES (6, '这里是u1的data desp', '2019-11-04 06:35:45', 4, 14, 'user1`s data', 'u1_1.txt', '2019-11-06 15:15:09');
INSERT INTO `resource` VALUES (7, 'here is u1`s data desp', '2019-11-04 06:36:19', 4, 15, 'u1`s second data', 'u1_2.txt', '2019-11-06 15:15:26');
INSERT INTO `resource` VALUES (8, 'this is user1`s third data desp', '2019-11-04 06:36:46', 4, 18, 'u1`s third data', 'u1_3.txt', '2019-11-06 15:15:43');
INSERT INTO `resource` VALUES (9, '这是u2的第一条数据描述', '2019-11-04 06:37:33', 5, 30, 'u2`s 1 data', 'u2_1.txt', '2019-11-06 15:18:22');
INSERT INTO `resource` VALUES (10, '这是u2的第二份数据描述', '2019-11-04 06:37:52', 5, 16, 'u2`s second data', 'u2_2.txt', '2019-11-06 15:21:35');
INSERT INTO `resource` VALUES (11, '这里是u2的第三份数据描述', '2019-11-04 06:38:30', 5, 18, 'u2的第三份数据', 'u2_3.txt', '2019-11-06 15:22:05');
INSERT INTO `resource` VALUES (12, '这里是u3的第一条数据描述', '2019-11-04 06:38:56', 6, 100, 'u3的第一条数据', 'u3_1.txt', '2019-11-06 15:27:47');
INSERT INTO `resource` VALUES (13, '这里是u3的第二条数据描述', '2019-11-04 06:39:35', 6, 1, 'u3的2数据描述', 'u3_2.txt', '2019-11-06 15:28:05');
INSERT INTO `resource` VALUES (14, 'u1上传了文件的第四份res data', '2019-11-06 03:04:14', 4, 100, 'u1`s 4 data', 'u1_4.txt', '2019-11-06 15:16:23');

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `email` varchar(120) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `password_hash` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `balance` int(11) DEFAULT NULL,
  `about_me` varchar(140) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `last_seen` datetime(0) DEFAULT NULL,
  `address` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `pub_key` varchar(64) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_user_email`(`email`) USING BTREE,
  UNIQUE INDEX `ix_user_username`(`username`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 9 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (3, 'kimroniny', '1301862177@qq.com', 'pbkdf2:sha256:150000$RxRacH3J$4f2ff67ee6864eea0fc2074215bb3827c3c86834b91e90a63595b9d5e69033c7', 100, NULL, '2019-11-07 00:49:25', '4696014cda52779b6e267e798f76e6a38819bb11', '04925b46fbc792645ae948d74696014cda52779b6e267e798f76e6a38819bb11');
INSERT INTO `user` VALUES (4, 'user1', 'user1@qq.com', 'pbkdf2:sha256:150000$yc0sWJ6K$230067ab2e5ff1994c116e1cd14cc2643a3a10c0af23cd14d875466608b03251', 100, NULL, '2019-11-06 23:25:47', 'fea902f76a1eaa9ebff07a631f66446281da8690', '9d13e6d0ad580a79edf88804fea902f76a1eaa9ebff07a631f66446281da8690');
INSERT INTO `user` VALUES (5, 'user2', 'user2@qq.com', 'pbkdf2:sha256:150000$nG6Rg7cs$119730a5d181c3e25add219671f5f5ec4ac2cf5b01c3224debfd600083c2db96', 115, NULL, '2019-11-06 23:25:09', 'f0459df653f1b6625fc07ec4b545775d43a46fc5', 'e5158c3f32c7169e2a14877bf0459df653f1b6625fc07ec4b545775d43a46fc5');
INSERT INTO `user` VALUES (6, 'user3', 'user3@qq.com', 'pbkdf2:sha256:150000$h4GQiDM2$57d3f6b1db9a82bd6884299ca6940734b126c98d894aef485e13826cf70feb81', 0, NULL, '2019-11-06 15:28:18', 'be076dd140d32003863ebf7d20fd71016269355b', '40213bc53f6e929b7240ca56be076dd140d32003863ebf7d20fd71016269355b');
INSERT INTO `user` VALUES (7, 'user4', 'user4@qq.com', 'pbkdf2:sha256:150000$Jn9FgQUe$206fe0dbca4343efe2b508314432adbff2bedf043d0b847bd411d5e7f30bbabc', 0, NULL, '2019-11-05 02:51:48', 'c4fbe470be313e211490fb557933038eed79826d', 'e033b1c6f20a26c7978edf6ec4fbe470be313e211490fb557933038eed79826d');
INSERT INTO `user` VALUES (8, 'user5', 'user5@qq.com', 'pbkdf2:sha256:150000$FwGHq3Pi$de4df2a605899320ebd79b695f87c09258f935c954535de87328851fcb127e0e', 100, NULL, '2019-11-06 23:24:29', '4aeab1826f8d3e8d7aea0c866bf6f12b6798495f', '6dff7c47475e5f59048f55614aeab1826f8d3e8d7aea0c866bf6f12b6798495f');

SET FOREIGN_KEY_CHECKS = 1;
