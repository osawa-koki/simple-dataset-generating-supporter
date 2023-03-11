
const USER_ID_REGEX = /^[a-zA-Z0-9_-]{3,8}$/;
const CATEGORY_REGEX = /^[a-zA-Z0-9_-]{3,8}$/;

const is_valid_both = (username: string, category: string) => {
  return USER_ID_REGEX.test(username) && CATEGORY_REGEX.test(category);
}
const is_valid_username = (username: string) => {
  return USER_ID_REGEX.test(username);
}
const is_valid_category = (category: string) => {
  return CATEGORY_REGEX.test(category);
}

export { is_valid_both, is_valid_username, is_valid_category, USER_ID_REGEX, CATEGORY_REGEX };
