| ↓ Session Store/ Auth Strategy → | Opaque | JWT | Basic | APIKey | Token |
| -------------------------------- | ------ | --- | ----- | ------ | ----- |
| In-Memory                        | O      | O   | O     | O      | O     |
| Redis                            | O      | O   | O     | X      | O     |
| Database                         | O      | O   | O     | O      | O     |
| Stateless                        | X      | O   | X     | X      | X     |

O = Supported
X = Not Supported

