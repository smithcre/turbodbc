#pragma once

#include <pydbc/description.h>

namespace pydbc {

/**
 * @brief Represents a description to bind a buffer holding double precision
 *        floating point values
 */
class floating_point_description : public description {
public:
	floating_point_description();
	~floating_point_description();
private:
	std::size_t do_element_size() const final;
	SQLSMALLINT do_column_c_type() const final;
	SQLSMALLINT do_column_sql_type() const final;
	field do_make_field(char const * data_pointer) const final;
};


}
